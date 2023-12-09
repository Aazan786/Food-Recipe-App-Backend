from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from recipes.serializers import RecipeSerializer, IngredientSerializer, FavouriteSerializer, ProfileSerilizer
from authapi.renderers import UserRenderer
from recipes.models import Recipe, Ingredient, Favourite, UserProfile
from rest_framework import serializers
from django.shortcuts import get_object_or_404




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


@api_view(['PUT', 'GET'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    if request.method == 'GET':
        user_profile = request.user.userprofile
        serializer =  ProfileSerilizer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        user_profile = request.user.userprofile
        serializer =  ProfileSerilizer(user_profile, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg':'Profile updated Successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=400)



@api_view(['POST'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def create_recipe(request):
    data = request.data
    serializer = RecipeSerializer(data=data, context={'request': request})

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({'msg':'Recipe created Successfully'}, status=status.HTTP_201_CREATED)
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            serializer = RecipeSerializer(recipe, many = False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
def add_to_favorites(request, pk):
    user_profile = request.user.userprofile
    recipe = Recipe.objects.get(id=pk)

    # Check if the recipe is already in favorites
    if Favourite.objects.filter(user_profile=user_profile, recipe=recipe).exists():
        return Response({'detail': 'Recipe is already in favorites.'}, status=status.HTTP_400_BAD_REQUEST)

    # If not, add it to favorites using the FavouriteSerializer
    serializer = FavouriteSerializer(data={'user_profile': user_profile.id, 'recipe': pk})
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
    favorite_recipes = Favourite.objects.filter(user_profile=user_profile)
    serializer = FavouriteSerializer(favorite_recipes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)