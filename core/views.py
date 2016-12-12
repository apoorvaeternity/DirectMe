from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import ShipStore, Version
from core.serializers import ShipStoreSerializer, VersionSerializer


class ShipsList(APIView):
    """
    Lists all ships along with complete details from the store.
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = ShipStoreSerializer

    def get(self, request):
        ships = ShipStore.objects.all()
        serializer = self.serializer_class(ships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShipsDetail(APIView):
    """
        Retrieves details of a ship along with complete details from the store.
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = ShipStoreSerializer

    def get(self, request, ship_id):
        ship = get_object_or_404(ShipStore, pk=ship_id)
        serializer = self.serializer_class(ship)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VersionCheck(APIView):
    """
    Version check at app startup
    """

    serializer_class = VersionSerializer

    def get(self, request):
        serializer = self.serializer_class(Version.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
