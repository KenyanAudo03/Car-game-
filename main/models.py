from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class GameProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    high_score = models.IntegerField(default=0)
    high_level = models.IntegerField(default=1)
    music_enabled = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
