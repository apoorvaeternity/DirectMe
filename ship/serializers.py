from rest_framework import serializers

from ship.models import Port, Ship


class PortsListSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(source='type.name')

    class Meta:
        model = Port
        fields = ('id', 'user', 'type')


class ShipsListSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ship_store.name')

    class Meta:
        model = Ship
        fields = ('id', 'name', 'raid_count')
