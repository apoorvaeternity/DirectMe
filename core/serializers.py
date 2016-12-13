from django.contrib.auth.models import User
from rest_framework import serializers

from core.models import ShipStore, ShipUpgrade, Version, DockChart, Dock, Port, Ship, PortType


class DockChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = DockChart
        fields = ('ship', 'start_time', 'end_time', 'is_success')


class DocksListSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ship_store.name')

    class Meta:
        model = Dock
        fields = ('__all__')


class DockShipSerializer(serializers.Serializer):
    ship_id = serializers.IntegerField()
    port_owner_id = serializers.IntegerField()
    port_type = serializers.CharField()

    def validate(self, attrs):
        ship_id = attrs['ship_id']
        try:
            ship = Ship.objects.get(pk=ship_id)
            if not (ship.is_idle() and ship.is_active and ship.belongs_to(self.context['request'].user)):
                raise serializers.ValidationError('Incorrect ship ID')
        except Ship.DoesNotExist:
            raise serializers.ValidationError('Ship with given ID doesnt exist')

        port_owner_id = attrs['port_owner_id']
        try:
            user = User.objects.get(pk=port_owner_id)
        except User.DoesNotExist:
            raise serializers.ValidationError('Port owner ID doesnt exist')

        port_type = attrs['port_type']
        try:
            PortType.objects.get(name=port_type)
        except PortType.DoesNotExist:
            raise serializers.ValidationError('Port type doesnt exist')

        try:
            print(user)
            # Port.objects.get()
        except:
            pass

        return attrs

    def save(self, **kwargs):
        DockChart.objects.create_entry(
            self.validated_data['ship_id'],
            self.validated_data['port_owner_id'],
            self.validated_data['port_type']
        )


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


class ShipUpgradeDetailSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='item_id.name')

    class Meta:
        model = ShipUpgrade
        fields = ('item_id', 'name', 'count')


class ShipStoreSerializer(serializers.ModelSerializer):
    items_required = ShipUpgradeDetailSerializer(many=True, read_only=True)

    class Meta:
        model = ShipStore
        fields = ('id', 'name', 'cost_multiplier', 'experience_gain', 'image', 'buy_cost', 'items_required')


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = '__all__'
