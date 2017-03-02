from decimal import Decimal
from random import randint

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from rest_framework.authtoken.models import Token

from core.models import Item, Island, Port, Dock
from core.models import Item, ShipStore


class ProfileModelManager(models.Manager):
    def create_player(self, username):
        user = User.objects.get(
            username=username
        )

        Profile.objects.create(user=user)

        Token.objects.create(user=user)

        Inventory.objects.create_initial_inventory(user=user)

        Port.objects.create_initial_ports(user=user)

        Dock.objects.create_initial_docks(user=user)

        ShipStore.objects.allocate_initial_ship(user=user)

        return user

    def add_exp(self, profile, exp):
        profile.experience += exp
        profile.save()

    def del_exp(self, profile, exp):
        profile.experience -= exp
        profile.save()

    def update_points(self, user):
        user = User.objects.get(username='user1')
        points = user.profile.points
        user_items = user.inventory.all()
        max_items = Inventory.objects.values('item').annotate(value=Max('count'))
        for item in user_items:
            points += Decimal(item.count) / Decimal(max_items.get(item=item.id)['value'])
        points += Decimal(user.profile.experience) / Decimal(
            Profile.objects.aggregate(Max('experience'))['experience__max'])
        user.profile.points = points
        user.profile.save()


class Profile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(default=None, null=True)
    experience = models.IntegerField(default=10)
    island = models.ForeignKey(Island, default=None, null=True)
    fcm_token = models.CharField(max_length=255, default=None, null=True, unique=True)
    points = models.DecimalField(default=0.0, max_digits=12, decimal_places=10)
    objects = ProfileModelManager()

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


class InventoryModelManager(models.Manager):
    def create_initial_inventory(self, user):
        for item in Item.objects.all():
            Inventory.objects.create(user=user, item=item, count=10)

    def add_item(self, user, item, value):
        inventory = Inventory.objects.get(user=user, item=item)
        inventory.count += value
        inventory.save()


class Inventory(models.Model):
    count = models.IntegerField()
    user = models.ForeignKey(User, related_name='inventory')
    item = models.ForeignKey(Item)

    objects = InventoryModelManager()

    class Meta:
        verbose_name_plural = 'Inventory'

    def __str__(self):
        return self.user.username + " : " + self.item.name + " : " + str(self.count)
