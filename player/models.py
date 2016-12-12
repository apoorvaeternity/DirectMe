from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from django.db import models

from core.models import Item, Island

from random import randint


class Profile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(default=None, null=True)
    experience = models.IntegerField(default=10)
    island = models.ForeignKey(Island, default=None, null=True)
    gcm_token = models.CharField(max_length=255, default=None, null=True, unique=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if self.island is None:
            self._set_random_island()

        return super(Profile, self).save()

    def _set_random_island(self):
        # TODO: Remove this hardcoding
        count = Island.objects.exclude(name='Pirate Island').count()
        # If not Island has been added yet, raise an error
        if count == 0:
            raise NotImplementedError

        random_island_id = randint(0, count - 1)

        self.island = Island.objects.exclude(name='Pirate Island')[random_island_id]

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

    class Meta:
        verbose_name_plural = 'Inventory'

    def __str__(self):
        return self.user.username + " : " + self.item.name + " : " + str(self.count)
