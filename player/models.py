from django.contrib.auth.models import User
from django.db import models

from core.models import Item, Island


class Profile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField()
    experience = models.IntegerField()
    island = models.ForeignKey(Island)
    gcm_token = models.CharField(max_length=255)
    auth_token = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username


class Inventory(models.Model):
    count = models.IntegerField()
    user = models.ForeignKey(User)
    item = models.ForeignKey(Item)

    def __str__(self):
        return self.user.username + " : " + self.item.name + " : " + str(self.count)
