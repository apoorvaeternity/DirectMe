from rest_framework import serializers

from ship.models import Port


class PortsListSerializer(serializers.ModelSerializer):

    type = serializers.ReadOnlyField(source='type.name')

    class Meta:
        model = Port
        fields = ('id', 'user', 'type')
