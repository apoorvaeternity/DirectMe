from django.db import models
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from core.models import Item, Island


class Profile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField()
    experience = models.IntegerField(default=1)
    island = models.ForeignKey(Island)
    gcm_token = models.CharField(max_length=255, default=None, null=True)

    def _set_random_island(self):
        pass

    def _set_default_avatar(self):
        pass

    def _create_auth_token(self):
        return Token.objects.create(self.user)

    def __str__(self):
        return self.user.username


class Inventory(models.Model):
    count = models.IntegerField()
    user = models.ForeignKey(User)
    item = models.ForeignKey(Item)

    def __str__(self):
        return self.item.name + str(self.count)
