from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from core.models import Dock, ShipStore, Port, PortType, Ship, DockChart
from player.models import Profile, Inventory


def setUpModule():
    print("Module setup...")
    call_command('loaddata', 'db.json', verbosity=0)


class DockPirateIslandTests(APITestCase):
    url = reverse('pirate-island')

    def test_invalid_ship(self):
        """Ensure the ship is incorrect"""

        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
                                      email='some_email@gmail.com')

        ship_id = 90
        data = {'ship_id': ship_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Ship with the given ID does not exist")

    def test_ship_active(self):
        """Ensure if ship is active"""
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
                                      email='some_email@gmail.com')
        ship = Ship.objects.get(user=user)
        ship.is_active = False
        ship.save()
        data = {'ship_id': ship.id}

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Ship doesn\'t exist")

    def test_ship_idle(self):
        """Ensure the ship is idle"""

        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
                                      email='some_email@gmail.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        pirate_port = Port.objects.create(user=user, type=PortType.objects.get(ownable=False))
        ship = Ship.objects.get(user=user)
        DockChart.objects.create(ship=ship, port=pirate_port)

        ship_id = ship.id

        data = {'ship_id': ship_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Ship is not idle")

    def test_pirate_port_exists(self):
        """Ensure pirate ports exists"""
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
                                      email='some_email@gmail.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        ship = Ship.objects.get(user=user)
        ship_id = ship.id

        data = {'ship_id': ship_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Pirate ports doesn\'t exist")

    def test_pirate_port_idle(self):
        """Ensure that atleast one pirate port is idle"""

        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
                                      email='some_email@gmail.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        pirate_port = Port.objects.create(user=user, type=PortType.objects.get(ownable=False))
        ship = Ship.objects.get(user=user)
        DockChart.objects.create(ship=ship, port=pirate_port)

        ship = Ship.objects.create(user=user, ship_store=ShipStore.objects.first())
        ship_id = ship.id

        data = {'ship_id': ship_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "No idle pirate port available")

    def test_dock_ship(self):
        """Ensure user can dock ship"""
        """Ensure that atleast one pirate port is idle"""

        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
                                      email='some_email@gmail.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        pirate_port = Port.objects.create(user=user, type=PortType.objects.get(ownable=False))
        ship = Ship.objects.get(user=user)
        ship_id = ship.id

        data = {'ship_id': ship_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        dock_chart = DockChart.objects.get(port=pirate_port, ship=ship)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(dock_chart.ship.ship_store.name, ship.ship_store.name)


class UpdateShipTests(APITestCase):
    url = reverse('update-ship')

    def test_ship_exists(self):
        """Ensure that ship exists"""

        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
                                      email='some_email@gmail.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        ship_id = 100

        data = {'ship_id': ship_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Ship with the given ID doesn\'t exist")

    def test_ship_idle(self):
        """Ensure that ship exists"""

        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
                                      email='some_email@gmail.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        ship = Ship.objects.get(user=user)
        port = Port.objects.filter(user=user).first()
        DockChart.objects.create(ship=ship, port=port)

        data = {'ship_id': ship.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Ship is not idle")


class BuyShipTests(APITestCase):
    url = reverse('buy-ship')

    def test_incorrect_dock_id(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
                                      email='some_email@gmail.com')
        docks = Dock.objects.filter(user=user)
        # Create incorrect dock_id
        dock_id = 0
        for dock in docks:
            dock_id += dock.id

        data = {'dock_id': dock_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Incorrect Dock ID")

    def test_lock_docked(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
                                      email='some_email@gmail.com')
        dock = Dock.objects.filter(user=user, ship=None).first()

        data = {'dock_id': dock.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Dock is not unlocked")

    def test_dock_already_occupied(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
                                      email='some_email@gmail.com')
        dock = Dock.objects.filter(user=user).exclude(ship=None).first()

        data = {'dock_id': dock.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Dock is already occupied")

    def test_insufficient_gold(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
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
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username', password=user.password,
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
