from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from player.models import Profile


def setUpModule():
    print("Module setup...")
    call_command('loaddata', 'db.json', verbosity=0)


class UserRegistrationTests(APITestCase):
    url = reverse('register')

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


class UserAuthenticationTests(APITestCase):
    url = reverse('login')

    def test_valid_user_auth(self):
        """
        Ensure we  get token in case of correct credentials
        """
        user = Profile.objects.create_player(username='some_username', password='some_password',
                                             email='some_email@gmail.com')
        data = {'username': 'some_username', 'password': 'some_password'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], user.auth_token.key)

    def test_invalid_user_auth(self):
        """
        Ensure we do not get token in case of wrong credentials
        """
        user = Profile.objects.create_player(username='some_username', password='some_password',
                                             email='some_email@gmail.com')
        data = {'username': 'some_username', 'password': 'wrong_password'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual('token' in response.data, False)


class UserViewTests(APITestCase):
    url = reverse('user')

    def test_get_user_details(self):
        """
        Ensure the user is setup properly and no unwanted details are revealed
        """
        user = Profile.objects.create_player(username='some_username', password='some_password',
                                             email='some_email@gmail.com')

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'some_username')
        self.assertEqual(response.data['email'], 'some_email@gmail.com')
        self.assertEqual(response.data['first_name'], '')
        self.assertEqual(response.data['last_name'], '')
        self.assertEqual(response.data['experience'], 10)
        self.assertEqual(len(response.data), 7)

    def test_update_user_details(self):
        """
        Ensure that the change in the fields are saved
        """
        user = Profile.objects.create_player(username='some_username', password='some_password',
                                             email='some_email@gmail.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        data = {'first_name': 'Jon'}
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Jon')
        self.assertEqual(response.data['last_name'], '')

        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Jon')


class GCMTokenViewTests(APITestCase):
    url = reverse('gcm')

    def test_update_gcm_token(self):
        """
        Ensure that the change in the GCM token are saved
        """
        user = Profile.objects.create_player(username='some_username', password='some_password',
                                             email='some_email@gmail.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        data = {'gcm_token': 'some_dragon_token_maybe'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.gcm_token, 'some_dragon_token_maybe')


class UserPasswordUpdateViewTests(APITestCase):
    url = reverse('reset-password')

    def test_update_passowrd(self):
        user = Profile.objects.create_player(username='some_username', password='some_password',
                                             email='some_email@gmail.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(user.auth_token.key))

        data = {'password': 'a_new_password'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {'username': 'some_username', 'password': 'a_new_password'}
        response = self.client.post(reverse('login'), data)
        user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], user.auth_token.key)
