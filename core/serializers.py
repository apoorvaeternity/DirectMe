from django.contrib.auth.models import User
from rest_framework import serializers

from core.models import ShipStore, ShipUpgrade, Version, DockChart, Dock, Port, Ship, FineLog, Level, Island
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
        # TODO: add cumulative ship level
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

        if not Port.objects.pirate_port_available():
            raise serializers.ValidationError('Pirate ports doesn\'t exist')

        if not DockChart.objects.is_available():
            raise serializers.ValidationError('No idle pirate port available')
        return attrs

    def create(self, validated_data):
        ship = Ship.objects.get(pk=validated_data['ship_id'])
        return DockChart.objects.allocate_pirate_port(ship)


class DockChartSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    ship_image = serializers.SerializerMethodField()

    def get_username(self, obj):
        username = Ship.objects.get(pk=obj.ship_id).user.username
        return username

    def get_user_id(self, obj):
        user_id = Ship.objects.get(pk=obj.ship_id).user_id
        return user_id

    def get_ship_image(self, obj):
        return obj.ship.ship_store.image.url

    class Meta:
        model = DockChart
        fields = ('ship', 'ship_image', 'start_time', 'end_time', 'is_success', 'username', 'user_id')


class DocksListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    ship_image = serializers.SerializerMethodField()
    island_id = serializers.SerializerMethodField()
    park_time = serializers.SerializerMethodField()
    port_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField('get_ship_status')
    user_id = serializers.IntegerField(source='user.id')
    dock_id = serializers.IntegerField(source='id')
    ship_id = serializers.IntegerField(source='ship.id')
    slot_id = serializers.IntegerField(source='slot.id')

    def get_name(self, obj):
        if Ship.objects.filter(pk=obj.ship_id).exists():
            return Ship.objects.get(pk=obj.ship_id).ship_store.name

    def get_ship_image(self, obj):
        if Ship.objects.filter(pk=obj.ship_id).exists():
            return Ship.objects.get(pk=obj.ship_id).ship_store.image.url

    def get_ship_status(self, obj):
        if DockChart.objects.filter(ship_id=obj.ship_id, end_time=None).exists():
            return "Busy"
        return "Idle"

    def get_island_id(self, obj):
        if DockChart.objects.filter(ship_id=obj.ship_id, end_time=None).exists():
            island_id = DockChart.objects.get(ship_id=obj.ship_id, end_time=None).port.user.profile.island_id
            return island_id

    def get_park_time(self, obj):
        if DockChart.objects.filter(ship_id=obj.ship_id, end_time=None).exists():
            park_time = DockChart.objects.get(ship_id=obj.ship_id, end_time=None).start_time
            return park_time

    def get_port_id(self, obj):
        if DockChart.objects.filter(ship_id=obj.ship_id, end_time=None).exists():
            port_id = DockChart.objects.get(ship_id=obj.ship_id, end_time=None).port.id
            return port_id

    def get_username(self, obj):
        if DockChart.objects.filter(ship_id=obj.ship_id, end_time=None).exists():
            username = DockChart.objects.get(ship_id=obj.ship_id, end_time=None).port.user.username
            return username

    class Meta:
        model = Dock
        fields = ('user_id', 'name', 'ship_image', 'island_id', 'park_time', 'port_id', 'username', 'status', 'dock_id',
                  'ship_id', 'slot_id')


class SuggestionListSerializer(serializers.Serializer):
    island_id = serializers.IntegerField()

    def validate(self, attrs):
        user = self.context['request'].user
        island = Island.objects.filter(pk=attrs['island_id'])

        if island.count() == 0:
            raise serializers.ValidationError('Island with the given ID doesn\'t exist')
        island = island.first()
        if not island.habitable:
            raise serializers.ValidationError('Given island is pirate island')

        users = User.objects.filter(profile__island=island)
        if user.profile.island.__eq__(island):
            users = users.exclude(id=user.id)

        if users.count() == 0:
            raise serializers.ValidationError('No user exists for the given island')

        attrs['users'] = users

        return attrs


class UpgradeShipSerializer(serializers.Serializer):
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

        ship_store = Ship.objects.get(pk=ship_id).ship_store
        if ShipStore.objects.order_by('buy_cost').last() == ship_store:
            raise serializers.ValidationError('Ship cannot be upgraded.')

        return attrs

    def update_ship(self):
        user = self.context['request'].user
        ship_id = self.validated_data['ship_id']
        ship = Ship.objects.get(pk=ship_id)
        next_ship_store = ShipUpgrade.objects.consume_inventory(ship, user)
        next_ship_instance = ship.update(next_ship_store=next_ship_store, user=user)
        Profile.objects.add_exp(user.profile, next_ship_store.experience_gain)
        # Update cumulative ship level

        level_delta = next_ship_instance.ship_store.ship_id - ship.ship_store.ship_id
        user.profile.cumulative_ship_level += level_delta
        user.profile.save()

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
        DockChart.objects.undock_ship(ship)


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
    port_id = serializers.IntegerField()

    def validate(self, attrs):
        ship_id = attrs['ship_id']
        try:
            ship = Ship.objects.get(pk=ship_id)
            if not (ship.is_idle() and ship.is_active and ship.belongs_to(self.context['request'].user)):
                raise serializers.ValidationError('Incorrect ship ID')
        except Ship.DoesNotExist:
            raise serializers.ValidationError('Ship with given ID doesn\'t exist')

        port_id = attrs['port_id']
        try:
            port_id = Port.objects.get(id=port_id).id
        except Port.DoesNotExist:
            raise serializers.ValidationError('Port does not exist.')

        port = Port.objects.get(id=port_id)

        if port.user == ship.user:
            raise serializers.ValidationError('Cant port on own Port')

        # initialize
        port_unoccupied = False
        if DockChart.objects.filter(port=port, end_time=None).count() == 0:
            port_unoccupied = True
        if not port_unoccupied:
            raise serializers.ValidationError('Port is busy.')

        return attrs

    def save(self, **kwargs):
        DockChart.objects.create_entry(
            self.validated_data['ship_id'],
            self.validated_data['port_id']
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
    status = serializers.SerializerMethodField('get_ship_status')
    island_id = serializers.SerializerMethodField()
    park_time = serializers.SerializerMethodField()
    port_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    ship_image = serializers.SerializerMethodField()

    def get_ship_status(self, obj):
        if DockChart.objects.filter(ship_id=obj, end_time=None).exists():
            return "Busy"
        return "Idle"

    def get_island_id(self, obj):
        if DockChart.objects.filter(ship_id=obj, end_time=None).exists():
            island_id = DockChart.objects.get(ship_id=obj, end_time=None).port.user.profile.island_id
            return island_id

    def get_park_time(self, obj):
        if DockChart.objects.filter(ship_id=obj, end_time=None).exists():
            park_time = DockChart.objects.get(ship_id=obj, end_time=None).start_time
            return park_time

    def get_port_id(self, obj):
        if DockChart.objects.filter(ship_id=obj, end_time=None).exists():
            port_id = DockChart.objects.get(ship_id=obj, end_time=None).port.id
            return port_id

    def get_username(self, obj):
        if DockChart.objects.filter(ship_id=obj, end_time=None).exists():
            username = DockChart.objects.get(ship_id=obj, end_time=None).port.user.username
            return username

    def get_ship_image(self, obj):
        return obj.ship_store.image.url

    class Meta:
        model = Ship
        fields = ('id', 'name', 'ship_image', 'raid_count', 'status', 'island_id', 'park_time', 'port_id', 'username')


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
