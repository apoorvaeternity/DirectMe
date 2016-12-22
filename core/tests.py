from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APITestCase

from player.models import Profile


def setUpModule():
    print("Module setup...")
    call_command('loaddata', 'db.json', verbosity=0)


class DockPirateIslandTests(APITestCase):
    url = reverse('pirate-island')

    def ship_not_idle(self):
        """
        Ensure the ship is idle
        """

        user = Profile.objects.create_player(username='some_username', password='some_password',
                                             email='some_email@gmail.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
