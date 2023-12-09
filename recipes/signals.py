from django.db.models.signals import post_save
from django.dispatch import receiver
from recipes.models import Recipe, UserProfile

@receiver(post_save, sender=Recipe)
def update_user_total_recipes(sender, instance, created, **kwargs):
    if created:
        # Increment the total_recipes field of the user's profile
        instance.owner.get_total_recipes()