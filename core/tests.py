from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Dock, ShipStore
from player.models import Profile, Inventory


def setUpModule():
    print("Module setup...")
    call_command('loaddata', 'db.json', verbosity=0)


class BuyShipTests(APITestCase):
    url = reverse('buy-ship')

    def test_incorrect_dock_id(self):
        user = Profile.objects.create_player(username='some_username', password='some_password',
                                             email='some_email@gmail.com')

        # TODO: fix the dock_id -- dont hardcode

        data = {'dock_id': '100'}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Incorrect Dock ID")

    def test_lock_docked(self):
        user = Profile.objects.create_player(username='some_username', password='some_password',
                                             email='some_email@gmail.com')

        dock = Dock.objects.filter(user=user, ship=None).first()

        data = {'dock_id': dock.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Dock is not unlocked")

    def test_dock_already_occupied(self):
        user = Profile.objects.create_player(username='some_username', password='some_password',
                                             email='some_email@gmail.com')

        dock = Dock.objects.filter(user=user).exclude(ship=None).first()

        data = {'dock_id': dock.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Dock is already occupied")

    def test_insufficient_gold(self):
        user = Profile.objects.create_player(username='some_username', password='some_password',
                                             email='some_email@gmail.com')

        dock = Dock.objects.filter(user=user, ship=None).first()

        # Increment players experience
        required_exp = dock.slot.unlock_level.experience_required
        user.profile.experience = required_exp
        user.profile.save()

        user.refresh_from_db()

        data = {'dock_id': dock.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "User doesn't have sufficient Gold")

    def test_buy(self):
        user = Profile.objects.create_player(username='some_username', password='some_password',
                                             email='some_email@gmail.com')

        dock = Dock.objects.filter(user=user, ship=None).first()

        # Increment player's experience
        required_exp = dock.slot.unlock_level.experience_required
        user.profile.experience = required_exp
        user.profile.save()

        user.refresh_from_db()

        # Increment player's gold
        required_gold = ShipStore.objects.order_by('buy_cost').first().buy_cost

        user_gold = Inventory.objects.filter(user=user, item__name__icontains='Gold').first()
        user_gold.count = required_gold
        user_gold.save()

        data = {'dock_id': dock.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        dock.refresh_from_db()
        user_gold.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(dock.ship != None, True)
        self.assertEqual(user_gold.count, 0)
