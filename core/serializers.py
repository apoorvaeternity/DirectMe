from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from core.models import ShipStore, ShipUpgrade, Version, DockChart, Dock, Port, Ship, PortType, FineLog, Level
from player.models import Profile


class BuyShipSerializer(serializers.Serializer):
    dock_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        dock_id = attrs['dock_id']

        dock = Dock.objects.filter(user=user, pk=dock_id).first()
        if dock is None:
            raise serializers.ValidationError("Incorrect Dock ID")
        # Calculate user's level
        user_experience = user.profile.experience
        user_level = Level.objects.filter(experience_required__lte=user_experience).order_by(
            '-experience_required').first().level_number

        # Check if dock is unlocked
        print(dock.slot.unlock_level.level_number)
        print(user_level)
        if dock.slot.unlock_level.level_number > user_level:
            raise serializers.ValidationError("Dock is not unlocked")

        # Check if dock is vacant or not
        if dock.ship is not None:
            raise serializers.ValidationError("Dock is already occupied")

        # Check if user has sufficient funds to buy raft or not
        from player.models import Inventory
        user_gold_count = Inventory.objects.filter(user=user, item__name__icontains='Gold').first().count
        buy_cost = ShipStore.objects.order_by('buy_cost').first().buy_cost
        if user_gold_count < buy_cost:
            raise serializers.ValidationError("User doesn't have sufficient Gold")

        return attrs

    def save(self):
        dock_id = self.validated_data['dock_id']
        dock = Dock.objects.get(pk=dock_id)
        dock.allocate_raft()


class DockPirateIslandSerializer(serializers.Serializer):
    ship_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        try:
            ship = Ship.objects.get(pk=attrs['ship_id'])
            if not ship.is_active:
                raise serializers.ValidationError('Ship doesn\'t exist')
            if not ship.is_idle():
                raise serializers.ValidationError('Ship is not idle')

        except Ship.DoesNotExist:
            raise serializers.ValidationError('Ship with the given ID does not exist')

        if Port.objects.pirate_port_available():
            raise serializers.ValidationError('Pirate ports doesn\'t exist')

        if not DockChart.objects.is_available():
            raise serializers.ValidationError('No idle pirate port available')
        return attrs

    def create(self, validated_data):
        ship = Ship.objects.get(pk=validated_data['ship_id'])
        return DockChart.objects.allocate_pirate_port(ship)


class DockChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = DockChart
        fields = ('ship', 'start_time', 'end_time', 'is_success')


class DocksListSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ship_store.name')

    class Meta:
        model = Dock
        fields = ('__all__')


class UpdateShipSerializer(serializers.Serializer):
    ship_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        ship_id = attrs['ship_id']
        try:
            ship = Ship.objects.get(pk=ship_id)
            if not ship.is_idle():
                raise serializers.ValidationError('Ship is not idle')
            if not (ship.is_active and ship.belongs_to(user)):
                raise serializers.ValidationError('Incorrect ship ID')
        except Ship.DoesNotExist:
            raise serializers.ValidationError('Ship with the given ID doesn\'t exist')

        if not ship.check_inventory(user):
            raise serializers.ValidationError('Insufficient items')

        return attrs

    def updateShip(self):
        user = self.context['request'].user
        ship_id = self.validated_data['ship_id']
        ship = Ship.objects.get(pk=ship_id)
        next_ship_store = ShipUpgrade.objects.consume_inventory(ship, user)
        next_ship_instance = ship.update(next_ship_store=next_ship_store, user=user)
        Profile.objects.add_exp(user.profile, next_ship_store.experience_gain)
        Dock.objects.update_ship_docked(ship, next_ship_instance)


class UndockSerializer(serializers.Serializer):
    ship_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        ship_id = attrs['ship_id']
        try:
            ship = Ship.objects.get(pk=ship_id)
            if ship.is_idle():
                raise serializers.ValidationError('Ship is idle')
            if not (ship.is_active and ship.belongs_to(self.context['request'].user)):
                raise serializers.ValidationError('Incorrect ship ID')
        except Ship.DoesNotExist:
            raise serializers.ValidationError('Ship with the given ID doesn\'t exist')
        return attrs

    def undock(self, request):
        ship_id = self.validated_data['ship_id']
        ship = Ship.objects.get(pk=ship_id)
        dock_chart = DockChart.objects.undock_ship(ship)

        # TODO: Change item generation formula
        time_fraction = timezone.now() - dock_chart.start_time
        minutes = time_fraction.total_seconds() / 60
        value = int(minutes) * dock_chart.ship.ship_store.cost_multiplier
        from player.models import Inventory
        Inventory.objects.add_item(user=request.user, item=dock_chart.port.user.profile.island.item, value=value)
        # TODO: Change exp gain formula
        Profile.objects.add_exp(request.user.profile, 50)


class FineSerializer(serializers.Serializer):
    port_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        port_id = attrs['port_id']
        try:
            port = Port.objects.get(pk=port_id)
            if port.is_penalisable():
                raise serializers.ValidationError('Port cannot be fined')
            if port.is_idle():
                raise serializers.ValidationError('Port with the given ID is idle')
        except Port.DoesNotExist:
            raise serializers.ValidationError('Port with the given ID does not exist')
        return attrs

    def fine(self, request):
        port_id = self.validated_data['port_id']
        port = Port.objects.get(pk=port_id)
        dock_chart = DockChart.objects.end_parking(port)
        # Todo remove static data
        Profile.objects.add_exp(request.user.profile, 20)
        Profile.objects.del_exp(dock_chart.ship.user.profile, 20)
        FineLog.objects.create_log(amount=20, dock_chart=dock_chart, )


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
            raise serializers.ValidationError('Ship with given ID doesn\'t exist')

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


from player.models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    item = serializers.ReadOnlyField(source='item.name', read_only=True)

    class Meta:
        model = Inventory
        fields = ('item', 'count',)


class ShipStoreSerializer(serializers.ModelSerializer):
    items_required = ShipUpgradeDetailSerializer(many=True, read_only=True)

    class Meta:
        model = ShipStore
        fields = ('id', 'name', 'cost_multiplier', 'experience_gain', 'image', 'buy_cost', 'items_required')


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = '__all__'
