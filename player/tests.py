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
