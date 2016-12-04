from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.authtoken.models import Token

from player.serializers import UserRegistrationSerializer, UserAuthenticationSeriaizer


class UserRegistrationView(APIView):
    """
    User Registration Endpoint
    """

    def post(self, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAuthenticationView(APIView):
    def post(self, request, *args, **kwargs):
        user = authenticate(
            username=request.data['username'],
            password=request.data['password']
        )

        if user is not None:
            return Response({"token": Token.objects.filter(user=user).first().key})

        return Response(status=status.HTTP_401_UNAUTHORIZED)


class User(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(request.user)
        return Response(serializer.data)
