from django.shortcuts import get_list_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ship.models import Port, Ship, Dock
from ship.serializers import PortsListSerializer, ShipsListSerializer, DocksListSerializer


class PortsList(APIView):
    """
    Retrieve all ports for a user.
    """

    def get(self, request):
        ports = get_list_or_404(Port, user_id=request.user.id)
        serializer = PortsListSerializer(ports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShipsList(APIView):
    """
    Retrieves all active ships of a user.
    """

    def get(self, request):
        ships = get_list_or_404(Ship, user_id=request.user.id, is_active=True)
        serializer = ShipsListSerializer(ships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DocksList(APIView):
    """
    Retrieves docks for the user.
    """

    def get(self, request):
        ships = get_list_or_404(Dock, user_id=request.user.id)
        serializer = DocksListSerializer(ships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        # 'all-ships': reverse('ship-list', request=request, format=format),
    })
