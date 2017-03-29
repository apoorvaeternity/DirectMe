from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Island
from player.models import Profile


def setUpModule():
    print("Module setup...")
    call_command('loaddata', 'db.json', verbosity=0)


class GoogleLoginTests(APITestCase):
    url = reverse('player:google-login', kwargs={'backend': 'google-oauth2'})

    def test_invalid_token(self):
        data = {'access_token': 'false_token'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserRegistrationTests(APITestCase):
    url = reverse('player:register')

    def test_register_user(self):
        """
        Ensure we can register a new user profile
        """

        data = {'username': 'some_username', 'email': 'some_email@gmail.com', 'password': 'some_password'}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Profile.objects.get().user.username, 'some_username')

    def test_email_required(self):
        """
        Ensure that email field is required and cannot be submitted blank
        """

        data = {'username': 'some_username', 'email': '', 'password': 'some_password'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Profile.objects.count(), 0)

        data = {'username': 'some_username', 'password': 'some_password'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Profile.objects.count(), 0)

    def test_unique_email(self):
        """
        Register the first user
        """

        data = {'username': 'some_username', 'email': 'some_email@gmail.com', 'password': 'some_password'}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Profile.objects.get().user.username, 'some_username')

        data = {'username': 'some_other_username', 'email': 'some_email@gmail.com',
                'password': 'some_password'}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], "A user with that email already exists.")


class UserAuthenticationTests(APITestCase):
    url = reverse('player:login')

    def test_valid_user_auth(self):
        """
        Ensure we  get token in case of correct credentials
        """
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        data = {'username': 'some_username', 'password': 'some_password'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], user.auth_token.key)

    def test_invalid_user_auth(self):
        """
        Ensure we do not get token in case of wrong credentials
        """
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        data = {'username': 'some_username', 'password': 'wrong_password'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual('token' in response.data, False)


class UserViewTests(APITestCase):
    url = reverse('player:user')

    def test_get_user_details(self):
        """
        Ensure the user is setup properly and no unwanted details are revealed
        """
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'some_username')
        self.assertEqual(response.data['email'], 'some_email@gmail.com')
        self.assertEqual(response.data['first_name'], '')
        self.assertEqual(response.data['last_name'], '')
        self.assertEqual(response.data['experience'], 10)
        self.assertEqual(len(response.data), 10)

    def test_update_user_details(self):
        """
        Ensure that the change in the fields are saved
        """
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        data = {'first_name': 'Jon'}
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Jon')
        self.assertEqual(response.data['last_name'], '')

        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Jon')

    def test_last_seen(self):
        """
        Ensure last_seen is updated on calling /core/ports/ API
        """
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        profile = Profile.objects.get(user=user)
        profile.last_seen += timezone.timedelta(minutes=40)
        profile.save()
        profile.refresh_from_db()

        # updating the last_seen of profile by 40 minutes
        self.assertEqual(profile.last_seen.minute, (timezone.now() + timezone.timedelta(minutes=40)).minute)

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        response = self.client.get(self.url)

        profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.last_seen.minute, timezone.now().minute)


class FCMTokenViewTests(APITestCase):
    url = reverse('player:fcm')

    def test_update_fcm_token(self):
        """
        Ensure that the change in the FCM token are saved
        """
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        data = {'fcm_token': 'some_dragon_token_maybe'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.fcm_token, 'some_dragon_token_maybe')


class UserPasswordUpdateViewTests(APITestCase):
    url = reverse('player:reset-password')

    def test_update_passowrd(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        data = {'password': 'a_new_password'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {'username': 'some_username', 'password': 'a_new_password'}
        response = self.client.post(reverse('player:login'), data)
        user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], user.auth_token.key)


class GetSuggestionTests(APITestCase):
    url = reverse('player:suggestions')

    def test_island_exists(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        data = {'island_id': 100}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Island with the given ID doesn't exist")

    def test_pirate_island(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        pirate_island = Island.objects.filter(name='Pirate Island').first()
        data = {'island_id': pirate_island.id}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Given island is pirate island")

    def test_vacant_users_available(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        data = {'island_id': Island.objects.get(name='Bamboo Island').id}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "No user exists for the given island")

    def test_get_list(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        user2 = User.objects.create_user(username='some_username2', password='some_password',
                                         email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username2')

        data = {'island_id': user2.profile.island.id}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]), 5)
        self.assertEqual(response.data[0]['user_id'], user2.id)
        self.assertEqual(response.data[0]['parking'], 2)
        self.assertEqual(response.data[0]['non_parking'], 3)
        self.assertEqual(response.data[0]['name'], 'some_username2')


class EmailSearchTest(APITestCase):
    url = None

    def test_email_required(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        self.url = reverse("player:search-email", kwargs={'email': user.email})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['email'], user.email)
        self.assertEqual(response.data['first_name'], "")
        self.assertEqual(response.data['last_name'], "")


class UsernameSearchTest(APITestCase):
    url = None

    def test_username_required(self):
        user = User.objects.create_user(username='some_username', password='some_password',
                                        email='some_email@gmail.com')
        Profile.objects.create_player(username='some_username')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        self.url = reverse("player:search-username", kwargs={'username': user.username})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['email'], user.email)
        self.assertEqual(response.data['first_name'], "")
        self.assertEqual(response.data['last_name'], "")
