from django.dispatch import receiver
from django.db.models.signals import post_save

from account.models import User, Profile


@receiver(signal=post_save, sender=User)
def create_profile(sender, **kwargs):
    instance = kwargs.get("instance")
    profile_instance = Profile.objects.create(user=instance)
    profile_instance.save()
