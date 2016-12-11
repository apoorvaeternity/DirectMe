from rest_framework import serializers

from ship.models import Port, Ship, Dock, DockChart


class DockChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = DockChart
        fields = ('ship', 'start_time', 'end_time', 'is_success')


class PortsListSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(source='type.name')
    logs = serializers.SerializerMethodField('get_logs_for_port')

    def get_logs_for_port(self, obj):
        docks = DockChart.objects.filter(end_time=None, port=obj)
        serializer = DockChartSerializer(docks, many=True)
        return serializer.data

    class Meta:
        model = Port
        fields = ('id', 'type', 'logs')


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
