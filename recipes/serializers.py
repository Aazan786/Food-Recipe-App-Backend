from rest_framework import serializers
from recipes.models import Recipe, Ingredient, Favourite, UserProfile
from authapi.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class ProfileSerilizer(serializers.ModelSerializer):
    # user = UserSerializer(many=False)
    class Meta:
        model = UserProfile
        fields = '__all__'
    # recipe_created = RecipeSerializer(many=True, read_only=True)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    owner = ProfileSerilizer(read_only=True)  # Use the owner's profile as read-only field

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ['featured_image']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])

        # Set the owner to the authenticated user's profile
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['owner'] = request.user.userprofile

        # Create the recipe instance
        recipe = Recipe.objects.create(**validated_data)

        # Save ingredients for the created recipe
        for ingredient_data in ingredients_data:
            ingredient_name = ingredient_data['name'].lower()

            # Check if the ingredient already exists
            ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)

            # Link the ingredient to the recipe
            recipe.ingredients.add(ingredient)

        return recipe


class FavouriteSerializer(serializers.ModelSerializer):
    creator = ProfileSerilizer(many=False, read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favourite
        fields = '__all__'


class FavouriteListSerializer(serializers.ModelSerializer):
    creator = ProfileSerilizer(many=False, read_only=True)
    recipe = RecipeSerializer(many=False, read_only=True)

    class Meta:
        model = Favourite
        fields = '__all__'
