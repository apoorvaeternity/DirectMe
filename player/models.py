from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField()
    experience = models.IntegerField()
    # island
    gcm_token = models.CharField(max_length=255)
    auth_token = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username
