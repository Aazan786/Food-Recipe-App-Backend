from authapi.models import User
from recipes.models import UserProfile
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, name=instance.name)

@receiver(post_save, sender=UserProfile)
def updateUser(sender, instance, created, **kwargs):
    userprofile = instance
    user = userprofile.user

    if created == False:
        user.name = userprofile.name
        user.save()


@receiver(post_delete, sender=UserProfile)
def delete_user(sender, instance, **kwargs):
    try:
        user = instance.user
        user.delete()
    except User.DoesNotExist:
        pass