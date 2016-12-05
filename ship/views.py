from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ship.models import Port
from ship.serializers import PortsListSerializer


class PortsList(APIView):
    """
    Retrieve all ports for a user.
    """

    def get_object(self, pk):
        try:
            return Port.objects.filter(user_id=pk)
        except Port.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        ports = self.get_object(pk)
        serializer = PortsListSerializer(ports, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        # 'all-ships': reverse('ship-list', request=request, format=format),
    })
