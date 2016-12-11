from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from player.serializers import UserRegistrationSerializer, UserAuthenticationSerializer, UserProfileSerializer, \
    UserGcmSerializer, UserPasswordSerializer


class UserRegistrationView(APIView):
    """
    User Registration Endpoint
    """

    def post(self, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAuthenticationView(APIView):
    """
    User login
    """

    def post(self, request, *args, **kwargs):
        serializer = UserAuthenticationSerializer(data=self.request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({'token': user.auth_token.key}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class UserView(APIView):
    """
    User Details
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
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

    def post(self, request):
        serializer = UserGcmSerializer(request.user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(self.request.user.profile, serializer.validated_data)
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordUpdateView(APIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = UserPasswordSerializer(data=request.data)

        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['password'])
            request.user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
