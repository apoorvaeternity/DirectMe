from django.shortcuts import get_list_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ship.models import Port, Ship, Dock
from ship.serializers import PortsListSerializer, ShipsListSerializer, DocksListSerializer


class PortsList(APIView):
    """
    Retrieve all ports for a user.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        ports = get_list_or_404(Port, user_id=request.user.id)
        serializer = PortsListSerializer(ports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShipsList(APIView):
    """
    Retrieves all active ships of a user.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        ships = get_list_or_404(Ship, user_id=request.user.id, is_active=True)
        serializer = ShipsListSerializer(ships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DocksList(APIView):
    """
    Retrieves docks for the user.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        ships = get_list_or_404(Dock, user_id=request.user.id)
        serializer = DocksListSerializer(ships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
