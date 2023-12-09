from django.contrib import admin
from .models import Recipe, Ingredient, Favourite, UserProfile


# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_recipes', 'get_total_recipes')

    # list_display = admin.ModelAdmin.list_display ("Totalrecipes")

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'owner', 'ingredient_names')


class IngridentsAdmin(admin.ModelAdmin):
    list_display = ('id','name')

class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('id','recipe', 'user_profile')



admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngridentsAdmin)
admin.site.register(Favourite, FavouriteAdmin)


