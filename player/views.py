from random import randint

from django.conf import settings
from django.contrib.auth.models import User
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from social_django.utils import psa

from core.models import Port
from core.serializers import SuggestionListSerializer
from player.models import Profile
from player.serializers import SocialSerializer


@api_view(http_method_names=['POST'])
@permission_classes([AllowAny])
@psa()
def exchange_token(request, backend):
    """
    Exchange an OAuth2 access token for one for this site.
    This simply defers the entire OAuth2 process to the front end.
    The front end becomes responsible for handling the entirety of the
    OAuth2 process; we just step in at the end and use the access token
    to populate some user identity.
    The URL at which this view lives must include a backend field, like:
        url(API_ROOT + r'social/(?P<backend>[^/]+)/$', exchange_token),
    Using that example, you could call this endpoint using i.e.
        POST API_ROOT + 'social/facebook/'
        POST API_ROOT + 'social/google-oauth2/'
    Note that those endpoint examples are verbatim according to the
    PSA backends which we configured in settings.py. If you wish to enable
    other social authentication backends, they'll get their own endpoints
    automatically according to PSA.
    ## Request format
    Requests must include the following field
    - `access_token`: The OAuth2 access token provided by the provider
    """
    serializer = SocialSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        # set up non-field errors key
        # http://www.django-rest-framework.org/api-guide/exceptions/#exception-handling-in-rest-framework-views
        try:
            nfe = settings.NON_FIELD_ERRORS_KEY
        except AttributeError:
            nfe = 'non_field_errors'

        try:
            # this line, plus the psa decorator above, are all that's necessary to
            # get and populate a user object for any properly enabled/configured backend
            # which python-social-auth can handle.
            user = request.backend.do_auth(serializer.validated_data['access_token'])
        except HTTPError as e:
            # An HTTPError bubbled up from the request to the social auth provider.
            # This happens, at least in Google's case, every time you send a malformed
            # or incorrect access key.
            return Response(
                {'errors': {
                    'token': 'Invalid token',
                    'detail': str(e),
                }},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user:
            if user.is_active:
                if not Profile.objects.filter(user=user).exists():
                    user = User.objects.get(username=user)
                    Profile.objects.create_player(username=user.username)
                return Response({'token': user.auth_token.key})
            else:
                # user is not active; at some point they deleted their account,
                # or were banned by a superuser. They can't just log in with their
                # normal credentials anymore, so they can't log in with social
                # credentials either.
                return Response(
                    {'errors': {nfe: 'This user account is inactive'}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Unfortunately, PSA swallows any information the backend provider
            # generated as to why specifically the authentication failed;
            # this makes it tough to debug except by examining the server logs.
            return Response(
                {'errors': {nfe: "Authentication Failed"}},
                status=status.HTTP_400_BAD_REQUEST,
            )


from player.serializers import UserRegistrationSerializer, UserAuthenticationSerializer, UserFcmSerializer, \
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

    authentication_classes = (TokenAuthentication,)
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


class FCMTokenView(APIView):
    """
    Register and update fcm token
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserFcmSerializer

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
    authentication_classes = (TokenAuthentication,)
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
    authentication_classes = (TokenAuthentication,)
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
    authentication_classes = (TokenAuthentication,)
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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, email, *args, **kwargs):
        if User.objects.filter(email=email).exists():
            serializer = self.serializer_class(User.objects.get(email=email))
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)
