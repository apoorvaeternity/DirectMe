from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from core.models import ShipStore
from core.serializers import ShipStoreSerializer


class ShipsList(APIView):
    """
    Lists all ships along with complete details from the store.
    """

    def get(self, request):
        ships = ShipStore.objects.all()
        serializer = ShipStoreSerializer(ships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShipsDetail(APIView):
    """
        Retrieves details of a ship along with complete details from the store.
    """

    def get(self, request):
        ship = get_object_or_404(ShipStore, pk=request.user.id)
        serializer = ShipStoreSerializer(ship)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'all-ships': reverse('ship-list', request=request, format=format),
    })
