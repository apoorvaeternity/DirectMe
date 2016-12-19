from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from player.models import Profile


# Create your tests here.

def setUpModule():
    print("Module setup...")
    call_command('loaddata', 'db.json', verbosity=0)


# def teardownModule():
#     print("Module teardown...")
#     call_command('flush', interactive=False, verbosity=0)


class ProfileTests(APITestCase):
    def test_register_user(self):
        """
        Ensure we can register a new user profile
        """

        url = reverse('register')
        data = {'username': 'shobhit', 'email': 'shobhit@gmail.com', 'password': 'directme'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Profile.objects.get().user.username, 'shobhit')

    def test_login(self):
        """
        Check login of user
        """

        # url = reverse('register')
        # data = {'username': 'shobhit', 'email': 'shobhit@gmail.com', 'password': 'directme'}
        # response = self.client.post(url, data)

        url = reverse('login')
        data = {'username': 'shobhit', 'password': 'wrongpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {'username': 'shobhit', 'password': 'directme'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
