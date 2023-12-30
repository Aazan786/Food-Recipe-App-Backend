from django.db import models
from authapi.models import User
from django.db.models import Count


# Create your models here.
class Ingredient(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    short_intro = models.CharField(max_length=200, blank=True, null=True)
    profile_image = models.ImageField(
        null=True, blank=True, upload_to='profile_images/', default="profile_images/user-default.png")
    total_recipes = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)

    def get_total_recipes(self):
        totalrecipes = Recipe.objects.filter(owner=self).count()
        self.total_recipes = totalrecipes
        self.save()

    class Meta:
        ordering = ['id']


class Recipe(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.PROTECT, null=True, related_name='recipe_created')
    ingredients = models.ManyToManyField(Ingredient)
    featured_image = models.ImageField(upload_to='recipes_images/', null=True, blank=True, default="default.jpg")
    title = models.CharField(max_length=200)
    instructions = models.TextField()

    def ingredient_names(self):
        return ', '.join(ingredient.name for ingredient in self.ingredients.all())

    def __str__(self):
        return self.title


class Favourite(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='creator')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, )
