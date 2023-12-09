from django.urls import path
from .views import*

app_name = "recipes"

urlpatterns = [
    path('profile', UserProfile, name = 'profile'),
    path('editprofile', update_user_profile, name = 'editprofile'),
    path('create_recipe', create_recipe, name='create_recipe'),
    path('update_recipe/<int:pk>', update_recipe, name='update_recipe'),
    path('get_all_recipes', get_all_recipes, name='get_all_recipes'),
    path('get_recipe_by_id/<int:pk>', get_recipe_by_id, name='get_recipe_by_id'),
    path('addtofavourite/<int:pk>', add_to_favorites, name='addtofavourite'),
    path('remove_from_favourite/<int:pk>', remove_from_favorites, name='remove_from_favourite'),
    path('get_favorite_recipes', get_favorite_recipes, name='get_favorite_recipes'),
]