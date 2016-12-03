from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from player.serializers import UserSerializer


class UserView(APIView):
    """
    User Registration Endpoint
    """

    def post(self, *args, **kwargs):
        serializer = UserSerializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
