from django.contrib.auth.models import User
from django.core.management import call_command
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Dock, ShipStore, Port, PortType, Ship, DockChart, ShipUpgrade
from player.models import Profile, Inventory, Item


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

        pirate_port = Port.objects.filter(user=User.objects.get(username='pirates'),
                                          type=PortType.objects.get(ownable=False)).first()
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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_pirate_port_idle(self):
        """Ensure that atleast one pirate port is idle"""

        pirate_ports = Port.objects.filter(user=User.objects.get(username='pirates'),
                                           type=PortType.objects.get(ownable=False))
        user_no = 1
        for port in pirate_ports:
            # Occupy all the available pirate ports
            user = User.objects.create_user(username='some_username' + str(user_no), password='some_password',
                                            email='some_email' + str(user_no) + '@gmail.com')
            Profile.objects.create_player(username='some_username' + str(user_no))
            self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
            ship = Ship.objects.get(user=user)
            DockChart.objects.create(ship=ship, port=port)
            user_no += 1
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        ship = Ship.objects.filter(user=user).first()
        ship_id = ship.id

        data = {'ship_id': ship_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "No idle pirate port available")

    def test_dock_ship(self):
        """Ensure user can dock ship"""

        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        pirate_port = Port.objects.filter(user=User.objects.get(username='pirates'),
                                          type=PortType.objects.get(ownable=False)).first()
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
        """Checks whether the ship to be upgraded is an active ship of the user."""

        user = User.objects._create_user(username='some_username', password='some_password',
                                         email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        ship = Ship.objects.get(user=user)
        Inventory.objects.add_item(user=user, item=Item.objects.get(name='Coconut'), value=10000)
        Inventory.objects.add_item(user=user, item=Item.objects.get(name='Banana'), value=10000)
        Inventory.objects.add_item(user=user, item=Item.objects.get(name='Bamboo'), value=10000)
        Inventory.objects.add_item(user=user, item=Item.objects.get(name='Timber'), value=10000)
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
        Inventory.objects.add_item(user=user, item=Item.objects.get(name='Coconut'), value=10000)
        Inventory.objects.add_item(user=user, item=Item.objects.get(name='Banana'), value=10000)
        Inventory.objects.add_item(user=user, item=Item.objects.get(name='Bamboo'), value=10000)
        Inventory.objects.add_item(user=user, item=Item.objects.get(name='Timber'), value=10000)
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

    def test_insufficient_gold(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        Profile.objects.add_exp(user.profile, 10000000)
        # Fetching the details of the docks updates the status of the docks to buy
        docks_url = reverse('docks')
        self.client.get(docks_url)
        dock = Dock.objects.filter(ship=None, status='buy').order_by('slot__gold').first()
        required_gold = dock.slot.gold
        user_gold = Inventory.objects.get(user=user, item__name='Gold')
        user_gold.count += required_gold
        user_gold.save()
        buy_slot_url = reverse('buy-slot')
        response = self.client.get(buy_slot_url)
        user_gold.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'ship_id': 2, 'pay_type': 'GOLD'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'User doesn\'t have sufficient Gold')

    def test_insufficient_resource(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        Profile.objects.add_exp(user.profile, 10000000)
        # Fetching the details of the docks updates the status of the docks to buy
        docks_url = reverse('docks')
        self.client.get(docks_url)
        dock = Dock.objects.filter(ship=None, status='buy').order_by('slot__gold').first()
        required_gold = dock.slot.gold
        user_gold = Inventory.objects.get(user=user, item__name='Gold')
        user_gold.count += required_gold
        user_gold.save()
        buy_slot_url = reverse('buy-slot')
        response = self.client.get(buy_slot_url)
        user_gold.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'ship_id': 2, 'pay_type': 'RESOURCE'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'User has insufficient Coconut,Timber,Banana,Bamboo')

    def test_buy(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        Profile.objects.add_exp(user.profile, 10000000)
        docks_url = reverse('docks')
        self.client.get(docks_url)
        dock = Dock.objects.filter(ship=None, status='buy').order_by('slot__gold').first()
        required_gold = dock.slot.gold
        user_gold = Inventory.objects.get(user=user, item__name='Gold')
        user_gold.count += required_gold
        user_gold.save()
        buy_slot_url = reverse('buy-slot')
        response = self.client.get(buy_slot_url)
        user_gold.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {'ship_id': 2, 'pay_type': 'GOLD'}
        user_gold = Inventory.objects.get(user=user, item__name='Gold')
        # Give lots of gold to buy ship
        user_gold.count += 1000000000
        user_gold.save()
        user_gold.refresh_from_db()

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


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
        ship = Ship.objects.get(user=user2)
        ships = ShipStore.objects.filter(buy_cost__gt=ship.ship_store.buy_cost).order_by('buy_cost')
        next_ship_store_id = ships.exclude(ship=ship).first().id
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ship_id'], ship_id)
        self.assertEqual(response.data[0]['name'], ship_name)
        self.assertEqual(response.data[0]['ship_image'], ship_image)
        self.assertEqual(response.data[0]['ship_status'], ship_status)
        self.assertEqual(response.data[0]['next_ship_store_id'], next_ship_store_id)

    def test_null_ship_status(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for dock in response.data:
            if dock['ship_id'] is None:
                self.assertEqual(dock['ship_status'], None)
            else:
                self.assertEqual(dock['ship_status'], 'Idle')


class BuySlotViewTest(APITestCase):
    url = reverse('buy-slot')

    def test_no_buyable_slot(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'No buyable slot.')

    def test_insufficient_gold(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        Profile.objects.add_exp(user.profile, 10000000)
        docks_url = reverse('docks')
        self.client.get(docks_url)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Insufficient gold.')

    def test_successful_buy(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        Profile.objects.add_exp(user.profile, 10000000)
        docks_url = reverse('docks')
        self.client.get(docks_url)
        dock = Dock.objects.filter(ship=None, status='buy').order_by('slot__gold').first()
        required_gold = dock.slot.gold
        user_gold = Inventory.objects.get(user=user, item__name='Gold')
        user_gold.count += required_gold
        initial_gold = user_gold.count
        user_gold.save()
        response = self.client.get(self.url)
        user_gold.refresh_from_db()
        final_gold = user_gold.count
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(initial_gold - final_gold, required_gold)


class ShipsListViewTest(APITestCase):
    url = reverse('ship-list')

    def test_required_inventory(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        index = 0
        for obj in ShipStore.objects.all().order_by('ship_lvl'):
            bamboo_required = ShipUpgrade.objects.filter(ship_store__ship_lvl__lte=obj.ship_lvl,
                                                         item_id__name='Bamboo').aggregate(Sum('count'))
            banana_required = ShipUpgrade.objects.filter(ship_store__ship_lvl__lte=obj.ship_lvl,
                                                         item_id__name='Banana').aggregate(Sum('count'))
            timber_required = ShipUpgrade.objects.filter(ship_store__ship_lvl__lte=obj.ship_lvl,
                                                         item_id__name='Timber').aggregate(Sum('count'))
            coconut_required = ShipUpgrade.objects.filter(ship_store__ship_lvl__lte=obj.ship_lvl,
                                                          item_id__name='Coconut').aggregate(Sum('count'))
            gold_required = ShipStore.objects.filter(ship_lvl__lte=obj.ship_lvl).aggregate(Sum('buy_cost'))

            self.assertEqual(response.data[index]['bamboo_required'], bamboo_required['count__sum'])
            self.assertEqual(response.data[index]['banana_required'], banana_required['count__sum'])
            self.assertEqual(response.data[index]['timber_required'], timber_required['count__sum'])
            self.assertEqual(response.data[index]['coconut_required'], coconut_required['count__sum'])
            self.assertEqual(response.data[index]['gold_required'], gold_required['buy_cost__sum'])

            index += 1
