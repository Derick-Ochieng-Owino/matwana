# signals.py in your app
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import MatwanaUser

@receiver(post_save, sender=User)
def create_matwana_user(sender, instance, created, **kwargs):
    """
    Automatically create a MatwanaUser profile when a new User is created
    """
    if created:
        MatwanaUser.objects.create(user=instance, role='passenger')

@receiver(post_save, sender=User)
def save_matwana_user(sender, instance, **kwargs):
    """
    Save the MatwanaUser profile when User is saved
    """
    try:
        instance.matwanauser.save()
    except MatwanaUser.DoesNotExist:
        MatwanaUser.objects.create(user=instance, role='passenger')