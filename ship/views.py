from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ship.models import Port, Ship
from ship.serializers import PortsListSerializer, ShipsListSerializer


class PortsList(APIView):
    """
    Retrieve all ports for a user.
    """

    def get_object(self, user):
        try:
            return Port.objects.filter(user_id=user)
        except Port.DoesNotExist:
            raise Http404

    def get(self, request):
        user = request.GET.get('user_id', 0)
        ports = self.get_object(user)
        serializer = PortsListSerializer(ports, many=True)
        return Response(serializer.data)


class ShipsList(APIView):
    """
    Retrieves all active ships of a user.
    """

    def get_object(self, user):
        try:
            return Ship.objects.filter(user_id=user, is_active=True)
        except Ship.DoesNotExist:
            raise Http404

    def get(self, request):
        user_id = request.GET.get('user_id', 0)
        ships = self.get_object(user_id)
        serializer = ShipsListSerializer(ships, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        # 'all-ships': reverse('ship-list', request=request, format=format),
    })
