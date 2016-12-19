from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import ShipStore, Version, Dock, Ship, Port
from core.serializers import ShipStoreSerializer, VersionSerializer, DocksListSerializer, DockShipSerializer, \
    PortsListSerializer, ShipsListSerializer, FineSerializer, UndockSerializer


class DocksListView(APIView):
    """
    Retrieves docks for the user.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = DocksListSerializer

    def get(self, request):
        ships = get_list_or_404(Dock, user_id=request.user.id)
        serializer = self.serializer_class(ships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DockShipView(APIView):
    """
    Dock Ship on someone else's port
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = DockShipSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(request):
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PortsListView(APIView):
    """
    Retrieve all ports for a user and show if any ship is docked on them or not.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = PortsListSerializer

    def get(self, request):
        ports = get_list_or_404(Port, user_id=request.user.id)
        serializer = self.serializer_class(ports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShipsListView(APIView):
    """
    Retrieves all active ships of a user.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = ShipsListSerializer

    def get(self, request):
        ships = get_list_or_404(Ship, user_id=request.user.id, is_active=True)
        serializer = self.serializer_class(ships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class FineView(APIView):
    """
    Fine a ship on your non-parking port
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = FineSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid(request):
            serializer.fine(request)
            return Response(status=status.HTTP_200_OK)


class UndockShipView(APIView):
    """
    Undock Ship from someone else's port
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = UndockSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data, context={'request': request})
        if serializer.is_valid(request):
            serializer.undock(request)
            return Response(status=status.HTTP_200_OK)
       