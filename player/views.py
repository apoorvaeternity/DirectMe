from random import randint

from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Port
from django.contrib.auth.models import User
from core.serializers import SuggestionListSerializer
from player.serializers import UserRegistrationSerializer, UserAuthenticationSerializer, UserGcmSerializer, \
    UserPasswordSerializer, UserProfileSerializer, UserSearchSerializer


class UserRegistrationView(APIView):
    """
    Register a new user
    """

    serializer_class = UserRegistrationSerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAuthenticationView(APIView):
    """
    Retrieve auth token for a user
    """
    serializer_class = UserAuthenticationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({'token': user.auth_token.key}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class UserView(APIView):
    """
    Get all user details
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(self.request.user, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GCMTokenView(APIView):
    """
    Register and update gcm token
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserGcmSerializer

    def post(self, request):
        serializer = self.serializer_class(request.user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(self.request.user.profile, serializer.validated_data)
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordUpdateView(APIView):
    """
    Update user's password
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['password'])
            request.user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SuggestionListView(APIView):
    """
    Get suggestions
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    serializer_class = SuggestionListSerializer

    def response_format(self, result, user, parking_ports, non_parking_ports):
        result.append({
            'name': user.username,
            'user_id': user.id,
            'parking': parking_ports,
            'non-parking': non_parking_ports
        })

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            data = serializer.validated_data['users']

            # initialize
            response = []
            count = data.count()
            while len(response) < min(5, count) and not len(data) == 0:

                random_index = randint(0, data.count() - 1)
                user = data[random_index]

                # remove already selected user from qureyset
                data = data.exclude(id=user.id)

                no_of_parking_ports = 0
                no_of_non_parking_ports = 0

                parking_ports = Port.objects.get_parking_ports(user)
                for port in parking_ports:
                    if port.is_idle():
                        no_of_parking_ports += 1

                non_parking_ports = Port.objects.get_non_parking_ports(user)
                for port in non_parking_ports:
                    if port.is_idle():
                        no_of_non_parking_ports += 1

                if not (no_of_non_parking_ports == 0 or non_parking_ports == 0):
                    self.response_format(response, user, no_of_parking_ports, no_of_non_parking_ports)
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsernameSearchView(APIView):
    """
    Check whether user exists using username and give some details
    """
    serializer_class = UserSearchSerializer
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, username, *args, **kwargs):
        if User.objects.filter(username=username).exists():
            serializer = self.serializer_class(User.objects.get(username=username))
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class EmailSearchView(APIView):
    """
    Check whether user exists using email and give some details
    """
    serializer_class = UserSearchSerializer
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, email, *args, **kwargs):
        if User.objects.filter(email=email).exists():
            serializer = self.serializer_class(User.objects.get(email=email))
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)
