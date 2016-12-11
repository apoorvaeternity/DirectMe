from rest_framework import serializers

from ship.models import Port, Ship, Dock


class PortsListSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(source='type.name')

    class Meta:
        model = Port
        fields = ('id', 'type')


class ShipsListSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ship_store.name')

    class Meta:
        model = Ship
        fields = ('id', 'name', 'raid_count')


class DocksListSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ship_store.name')

    class Meta:
        model = Dock
        fields = ('__all__')


class DockShipSerializer(serializers.Serializer):
    ship_id = serializers.IntegerField()
    port_owner_id = serializers.IntegerField()
    port_type = serializers.CharField()
