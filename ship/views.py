from django.contrib.auth.models import User
from django.shortcuts import get_list_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from player.models import Inventory
from ship.models import Port, Ship, Dock, DockChart
from ship.serializers import PortsListSerializer, ShipsListSerializer, DocksListSerializer, DockShipSerializer


class FineView(APIView):
    """
    Fine a ship on your non-parking port
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, port_id):
        port = Port.objects.get(pk=port_id)
        if port.type.name == "Parking":
            return Response(status=status.HTTP_400_BAD_REQUEST)
        dock_chart_instance = DockChart.objects.filter(port=port, end_time=None).first()

        # No ship standing on this
        if dock_chart_instance is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # End the parking
        dock_chart_instance.end_time = timezone.now()
        dock_chart_instance.is_success = False
        dock_chart_instance.save()

        self.request.user.profile.experience += 20

        # TODO: Check for non negative exp
        dock_chart_instance.ship.user.profile.experience -= 20

        self.request.user.profile.save()
        dock_chart_instance.ship.user.profile.save()
        return Response(status=status.HTTP_200_OK)


class PortsListView(APIView):
    """
    Retrieve all ports for a user and show if any ship is docked on them or not.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        ports = get_list_or_404(Port, user_id=request.user.id)
        serializer = PortsListSerializer(ports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShipsListView(APIView):
    """
    Retrieves all active ships of a user.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        ships = get_list_or_404(Ship, user_id=request.user.id, is_active=True)
        serializer = ShipsListSerializer(ships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DocksListView(APIView):
    """
    Retrieves docks for the user.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        ships = get_list_or_404(Dock, user_id=request.user.id)
        serializer = DocksListSerializer(ships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DockShipView(APIView):
    """
    Dock Ship on someone else's port
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        serializer = DockShipSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ship_id = serializer.validated_data['ship_id']
        port_owner_id = serializer.validated_data['port_owner_id']
        port_type = serializer.validated_data['port_type']
        ship = Ship.objects.get(pk=ship_id)

        if not (ship.is_idle() and ship.is_active and ship.belongs_to(user=request.user)):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ports = Port.objects.filter(user=User.objects.get(pk=port_owner_id), type__name=port_type)
        for port in ports:
            logs = DockChart.objects.filter(port=port, end_time=None)
            if logs.count() == 0:
                log = DockChart(start_time=timezone.now(), ship=ship, port=port)
                log.save()
                port.log = log
                port.save()
                return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class UndockShipView(APIView):
    """
    Undock Ship from someone else's port
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, ship_id):
        ship_instance = Ship.objects.filter(pk=ship_id, user=request.user, is_active=True).first()

        if ship_instance is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        dock_chart_instance = DockChart.objects.filter(ship=ship_instance, end_time=None).first()
        if dock_chart_instance is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        dock_chart_instance.end_time = timezone.now()
        dock_chart_instance.is_success = True
        dock_chart_instance.save()

        island = dock_chart_instance.port.user.profile.island
        item_instance = Inventory.objects.get(user=request.user, item=island.item)

        # TODO: Change item generation formula
        time_fraction = timezone.now() - dock_chart_instance.start_time
        minutes = time_fraction.total_seconds() / 60
        value = int(minutes) * dock_chart_instance.ship.ship_store.cost_multiplier
        item_instance.count += value

        item_instance.save()

        # TODO: Change exp gain formula
        request.user.profile.experience += 50
        request.user.profile.save()

        return Response(status=status.HTTP_200_OK)
