from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, renderer_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from recipes.serializers import RecipeSerializer, IngredientSerializer, FavouriteSerializer, ProfileSerilizer, \
    FavouriteListSerializer
from authapi.renderers import UserRenderer
from recipes.models import Recipe, Ingredient, Favourite, UserProfile
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser


# Create your views here.
# @api_view(['GET'])
# @renderer_classes([UserRenderer])
# @permission_classes([IsAuthenticated])
# def UserProfile(request):
#     user_profile = request.user.userprofile
#     serializer =  ProfileSerilizer(user_profile)
#     return Response(serializer.data, status=status.HTTP_200_OK)


class ExtendedProfileSerializer(ProfileSerilizer):
    recipe_created = RecipeSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'


@api_view(['GET'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def UserProfile(request):
    user_profile = request.user.userprofile
    serializer = ExtendedProfileSerializer(user_profile)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user_profile = request.user.userprofile

    if request.method == 'PUT':
        serializer = ProfileSerilizer(user_profile, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            # Save profile information
            serializer.save()

            # Handle profile image upload
            profile_image = request.data.get('profile_image')
            if profile_image:
                user_profile.profile_image = profile_image
                user_profile.save()

            updated_serializer = ExtendedProfileSerializer(user_profile)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def create_recipe(request):
    data = request.data
    print('Received data:', data)  # Add this line for debugging

    serializer = RecipeSerializer(data=data, context={'request': request})

    if serializer.is_valid(raise_exception=True):
        # Save the recipe
        serializer.save()

        # Retrieve the recipe_id from the saved instance
        recipe_id = serializer.instance.id

        return Response({'msg': 'Recipe created Successfully', 'recipe_id': recipe_id}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_recipe_image(request):
    try:
        recipe_id = request.data.get('recipe_id')
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)

    image_data = request.data.get('image')
    if not image_data:
        return Response({'error': 'Image data not provided'}, status=status.HTTP_400_BAD_REQUEST)

    # Save the image to the recipe instance
    recipe.featured_image = image_data
    recipe.save()

    return Response({'msg': 'Image uploaded successfully'}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def update_recipe(request, pk):
    recipe_instance = get_object_or_404(Recipe, id=pk)
    data = request.data
    serializer = RecipeSerializer(recipe_instance, data=data, context={'request': request}, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({'msg': 'Recipe updated successfully'}, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def get_all_recipes(request):
    recipes = Recipe.objects.all()
    serializer = RecipeSerializer(recipes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def get_recipe_by_id(request, pk):
    try:
        recipe = Recipe.objects.get(id=pk)
        serializer = RecipeSerializer(recipe, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Recipe.DoesNotExist:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)


from django.http import Http404


@api_view(['POST'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def add_to_favorites(request, pk):
    user_profile = request.user.userprofile
    # print(user_profile)

    try:
        recipe = Recipe.objects.get(id=pk)
        # print(recipe)
    except Recipe.DoesNotExist:
        raise Http404("Recipe not found")

    # Check if the recipe is already in favorites
    if Favourite.objects.filter(user_profile=user_profile, recipe=recipe).exists():
        return Response({'detail': 'Recipe is already in favorites.'}, status=status.HTTP_400_BAD_REQUEST)

    # If not, add it to favorites using the FavouriteSerializer
    serializer = FavouriteSerializer(data={'user_profile': user_profile.id, 'recipe': recipe.id})
    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'Recipe added to favorites.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def remove_from_favorites(request, pk):
    user_profile = request.user.userprofile
    recipe = Recipe.objects.get(id=pk)

    # Check if the recipe is in favorites
    favorite = Favourite.objects.filter(user_profile=user_profile, recipe=recipe).first()
    if not favorite:
        return Response({'detail': 'Recipe is not in favorites.'}, status=status.HTTP_400_BAD_REQUEST)

    # If it is, remove it from favorites using the FavouriteSerializer
    serializer = FavouriteSerializer(instance=favorite)
    favorite.delete()
    return Response({'detail': 'Recipe removed from favorites.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def get_favorite_recipes(request):
    user_profile = request.user.userprofile
    favorites = Favourite.objects.filter(user_profile=user_profile)
    serializer = FavouriteListSerializer(favorites, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def check_favorite(request, recipe_id):
    try:
        user_profile = request.user.userprofile
        is_favorite = Favourite.objects.filter(user_profile=user_profile, recipe_id=recipe_id).exists()
        return Response({'isFavorite': is_favorite})
    except Exception as e:
        return Response({'error': str(e)}, status=500)
