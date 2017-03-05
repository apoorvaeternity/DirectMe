from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

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
        Profile.objects.create_player(username='some_username')

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
        Profile.objects.create_player(username='some_username')
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
        Profile.objects.create_player(username='some_username')
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
        Profile.objects.create_player(username='some_username')
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
        Profile.objects.create_player(username='some_username')
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
        Profile.objects.create_player(username='some_username')
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


class UpgradeShipTests(APITestCase):
    url = reverse('upgrade-ship')

    def test_ship_exists(self):
        """Ensure that ship exists"""

        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
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
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        ship = Ship.objects.get(user=user)
        port = Port.objects.filter(user=user).first()
        DockChart.objects.create(ship=ship, port=port)

        data = {'ship_id': ship.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Ship is not idle")

    def test_ship_belongs_user(self):
        """Ensure that the ship belongs to user"""

        # User 1
        user = User.objects._create_user(username='some_username', password='some_password',
                                         email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        ship = Ship.objects.get(user=user)

        # User 2
        user2 = User.objects._create_user(username='some_username2', password='some_password',
                                          email='some_email2@gmail.com')
        Profile.objects.create_player(username='some_username2')

        data = {'ship_id': ship.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user2.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Incorrect ship ID")

    def test_ship_active(self):
        """Ensure that the ship is active"""

        user = User.objects._create_user(username='some_username', password='some_password',
                                         email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        ship = Ship.objects.get(user=user)

        data = {'ship_id': ship.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Incorrect ship ID")

    def test_upgrade_ship(self):
        """Ensure that the sufficient items are present for updating ship"""

        user = User.objects._create_user(username='some_username', password='some_password',
                                         email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        ship_id = Ship.objects.get(user=user).id

        initial_cumulative_level = user.profile.cumulative_ship_level

        data = {'ship_id': ship_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        ship = Ship.objects.get(id=ship_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ship.is_active, False)

        ship = Ship.objects.get(user=user, is_active=True)
        self.assertNotEqual(ship.id, ship_id)

        user = User.objects.get(username='some_username')
        final_cumulative_level = user.profile.cumulative_ship_level
        self.assertGreater(final_cumulative_level, initial_cumulative_level)

    def test_max_ship(self):
        """Ensure that ship cannot be upgraded after the last ship is reached"""

        user = User.objects._create_user(username='some_username', password='some_password',
                                         email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        ship = Ship.objects.get(user=user, is_active=True)
        ship.ship_store = ShipStore.objects.order_by('buy_cost').last()
        ship.save()

        data = {'ship_id': ship.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Ship cannot be upgraded.")


class BuyShipTests(APITestCase):
    url = reverse('buy-ship')

    def test_incorrect_dock_id(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
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
        Profile.objects.create_player(username='some_username')
        dock = Dock.objects.filter(user=user, ship=None).first()

        data = {'dock_id': dock.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Dock is not unlocked")

    def test_dock_already_occupied(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        dock = Dock.objects.filter(user=user).exclude(ship=None).first()

        data = {'dock_id': dock.id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Dock is already occupied")

    def test_insufficient_gold(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
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
        Profile.objects.create_player(username='some_username')
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


class DockShipTest(APITestCase):
    url = reverse('dock-ship')

    def test_dock(self):
        # Test whether ships can be docked on other ports
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        user2 = User.objects.create_user(username='some_username2', password='some_password',
                                         email='some_email2@gmail.com')
        Profile.objects.create_player(username='some_username2')
        ship_id = Ship.objects.get(user=user2).id
        port_id = Port.objects.filter(user=user).first().id

        # Parking user2's raft on user's port
        data = {'ship_id': ship_id, 'port_id': port_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user2.auth_token.key))
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_wrong_port(self):
        # Test wrong port
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        user2 = User.objects.create_user(username='some_username2', password='some_password',
                                         email='some_email2@gmail.com')
        Profile.objects.create_player(username='some_username2')
        ship_id = Ship.objects.get(user=user2).id

        # Parking user2's raft on user's port
        data = {'ship_id': ship_id, 'port_id': 99999}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user2.auth_token.key))
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Port does not exist.")

    def test_port_on_own_port(self):
        # Trying to port own ship on own Port
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        ship_id = Ship.objects.get(user=user).id
        port_id = Port.objects.filter(user=user).first().id

        data = {'ship_id': ship_id, 'port_id': port_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Cant port on own Port")


class CorePortTest(APITestCase):
    url = None

    def test_port_details(self):
        dock_url = reverse('dock-ship')
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        user2 = User.objects.create_user(username='some_username2', password='some_password',
                                         email='some_email2@gmail.com')
        Profile.objects.create_player(username='some_username2')
        ship_id = Ship.objects.get(user=user2).id
        port_id = Port.objects.filter(user=user, type__penalizable=False).first().id
        # Parking user2's raft on user's port
        data = {'ship_id': ship_id, 'port_id': port_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user2.auth_token.key))
        self.client.post(dock_url, data)
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        self.url = reverse('ports', kwargs={'user_id': user.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]['id'], port_id)
        self.assertEqual(response.data[0]['type'], "Parking")
        self.assertEqual(response.data[0]['logs'][0]['ship'], ship_id)
        self.assertEqual(response.data[0]['logs'][0]['username'], user2.username)
        self.assertEqual(response.data[0]['logs'][0]['user_id'], user2.id)

    def test_no_userid(self):
        # Passing no user_id in kwargs
        dock_url = reverse('dock-ship')
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        user2 = User.objects.create_user(username='some_username2', password='some_password',
                                         email='some_email2@gmail.com')
        Profile.objects.create_player(username='some_username2')
        ship_id = Ship.objects.get(user=user2).id
        port_id = Port.objects.filter(user=user, type__penalizable=False).first().id
        # Parking user2's raft on user's port
        data = {'ship_id': ship_id, 'port_id': port_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user2.auth_token.key))
        self.client.post(dock_url, data)
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        self.url = reverse('ports')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]['id'], port_id)
        self.assertEqual(response.data[0]['type'], "Parking")
        self.assertEqual(response.data[0]['logs'][0]['ship'], ship_id)
        self.assertEqual(response.data[0]['logs'][0]['username'], user2.username)
        self.assertEqual(response.data[0]['logs'][0]['user_id'], user2.id)

    def test_port_others(self):
        # Test details of other's ports
        dock_url = reverse('dock-ship')
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        user2 = User.objects.create_user(username='some_username2', password='some_password',
                                         email='some_email2@gmail.com')
        Profile.objects.create_player(username='some_username2')
        ship_id = Ship.objects.get(user=user2).id
        port_id = Port.objects.filter(user=user, type__penalizable=False).first().id
        # Parking user2's raft on user's port
        data = {'ship_id': ship_id, 'port_id': port_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user2.auth_token.key))
        self.client.post(dock_url, data)
        self.url = reverse('ports', kwargs={'user_id': user.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]['id'], port_id)
        self.assertEqual(response.data[0]['type'], "Parking")
        self.assertEqual(response.data[0]['logs'][0]['ship'], ship_id)
        self.assertEqual(response.data[0]['logs'][0]['username'], user2.username)
        self.assertEqual(response.data[0]['logs'][0]['user_id'], user2.id)


class ShipsListViewTest(APITestCase):
    url = reverse('player:ships')

    def test_port_details(self):
        dock_url = reverse('dock-ship')
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        user2 = User.objects.create_user(username='some_username2', password='some_password',
                                         email='some_email2@gmail.com')
        Profile.objects.create_player(username='some_username2')
        ship_id = Ship.objects.get(user=user2).id
        port_id = Port.objects.filter(user=user).first().id
        # Parking user2's raft on user's port
        data = {'ship_id': ship_id, 'port_id': port_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user2.auth_token.key))
        self.client.post(dock_url, data)
        name = Ship.objects.get(id=ship_id).ship_store.name
        response = self.client.get(self.url)
        raid_count = Ship.objects.get(id=ship_id).raid_count
        ship_status = "Idle"
        if DockChart.objects.filter(ship_id=ship_id, end_time=None).exists():
            ship_status = "Busy"
        port_id = DockChart.objects.get(ship_id=ship_id, end_time=None).port.id
        username = DockChart.objects.get(ship_id=ship_id, end_time=None).port.user.username
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], name)
        self.assertEqual(response.data[0]['status'], ship_status)
        self.assertEqual(response.data[0]['raid_count'], raid_count)
        self.assertEqual(response.data[0]['port_id'], port_id)
        self.assertEqual(response.data[0]['username'], username)


class UndockShipTest(APITestCase):
    url = reverse('undock')

    def test_undock(self):
        dock_url = reverse('dock-ship')
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        user2 = User.objects.create_user(username='some_username2', password='some_password',
                                         email='some_email2@gmail.com')
        Profile.objects.create_player(username='some_username2')
        ship_id = Ship.objects.get(user=user2).id
        port_id = Port.objects.filter(user=user, type__penalizable=False).first().id
        # Parking user2's raft on user's port
        data = {'ship_id': ship_id, 'port_id': port_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user2.auth_token.key))
        self.client.post(dock_url, data)
        data = {'ship_id': ship_id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auto_undock(self):
        dock_url = reverse('dock-ship')
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        user2 = User.objects.create_user(username='some_username2', password='some_password',
                                         email='some_email2@gmail.com')
        Profile.objects.create_player(username='some_username2')
        ship_id = Ship.objects.get(user=user2).id
        port_id = Port.objects.filter(user=user, type__penalizable=False).first().id
        # Parking user2's raft on user's port
        data = {'ship_id': ship_id, 'port_id': port_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user2.auth_token.key))
        response = self.client.post(dock_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        dock = DockChart.objects.get(ship_id=ship_id, end_time=None)
        dock.start_time -= timezone.timedelta(minutes=40)
        dock.save()
        dock.refresh_from_db()

        ships_url = reverse('player:ships')
        response = self.client.get(ships_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['status'], "Idle")
        self.assertEqual(response.data[0]['name'], "Raft")


class DockListViewTest(APITestCase):
    url = reverse('docks')

    def test_docks_details(self):
        dock_url = reverse('dock-ship')
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        user2 = User.objects.create_user(username='some_username2', password='some_password',
                                         email='some_email2@gmail.com')
        Profile.objects.create_player(username='some_username2')
        ship_id = Ship.objects.get(user=user2).id
        port_id = Port.objects.filter(user=user, type__penalizable=False).first().id
        # Parking user2's raft on user's port
        data = {'ship_id': ship_id, 'port_id': port_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user2.auth_token.key))
        response = self.client.post(dock_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        docks_url = reverse('docks')
        response = self.client.get(docks_url)
        ship_name = Ship.objects.get(pk=ship_id).ship_store.name
        ship_image = Ship.objects.get(pk=ship_id).ship_store.image.url
        ship_status = "Idle"
        if DockChart.objects.filter(ship_id=ship_id, end_time=None).exists():
            ship_status = "Busy"
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[1]['ship_id'], ship_id)
        self.assertEqual(response.data[1]['name'], ship_name)
        self.assertEqual(response.data[1]['ship_image'], ship_image)
        self.assertEqual(response.data[1]['status'], ship_status)


    def test_null_ship_status(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for dock in response.data:
            if dock['ship_id'] is None:
                self.assertEqual(dock['status'], None)
            else:
                self.assertEqual(dock['status'], 'Idle')