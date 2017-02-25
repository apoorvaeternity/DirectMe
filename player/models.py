from uuid import uuid4
from random import randint
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from rest_framework.authtoken.models import Token

from core.models import Item, Island, Port, Dock
from core.models import Item, ShipStore


# from player.models import Profile, Inventory
# from ship.models import Port, Dock


class ProfileModelManager(models.Manager):

    def create_player(self, username, password, email):
        user = User.objects.get(
            username=username,
            password=password,
            email=email
        )

        Profile.objects.create(user=user)

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


class Profile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(default=None, null=True)
    experience = models.IntegerField(default=10)
    island = models.ForeignKey(Island, default=None, null=True)
    gcm_token = models.CharField(max_length=255, default=None, null=True, unique=True)
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


class EmailVerificationModelManager(models.Manager):
    def create_verification_link(user):
        token = str(uuid4())
        email = user.email
        verification_link = "https://direct-me.herokuapp.com/user/email-verification/" + token + "/"
        send_mail("Verification Link", "Verify your email.",
                  settings.EMAIL_HOST_USER, [email],
                  fail_silently=False, html_message="<a href=" + verification_link + ">\
                  Click here to verify your account for DirectMe.</a>")
        quer = EmailVerification(token=token, email=email, user=user)
        quer.save()

    def verify_token(token):
        query = EmailVerification.objects.get(token=token)
        query.verified = True
        query.save()


class EmailVerification(models.Model):
    user = models.ForeignKey(User, default=None)
    email = models.EmailField()
    token = models.CharField(max_length=50)
    verified = models.BooleanField(default=False)
