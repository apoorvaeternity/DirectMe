from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class DockModelManager(models.Manager):
    def create_initial_docks(self, user):
        """
        Setup initial docs for a new user
        """
        for slot in Slot.objects.all():
            Dock.objects.create(user=user, slot=slot)

    def unlock_first_dock(self, user):
        """
        Returns first unlocked dock
        """
        return Dock.objects.filter(user=user).order_by('slot__unlock_level').first()

    def update_ship_docked(self, previous_ship, current_ship):
        dock_instance = Dock.objects.get(ship=previous_ship)
        dock_instance.ship = current_ship
        dock_instance.save()


# Garage
class Dock(models.Model):
    user = models.ForeignKey(User, related_name='dock')
    slot = models.ForeignKey('Slot', related_name='slot')
    ship = models.ForeignKey('Ship', default=None, null=True)

    objects = DockModelManager()

    def allocate_raft(self):
        # Assign raft here

        ship = ShipStore.objects.buy_raft(user=self.user)
        self.ship = ship
        self.save()

        return ship


class DockChartModelManager(models.Manager):
    def create_entry(self, ship_id,  port_id):
        return DockChart.objects.create(
            ship=Ship.objects.get(pk=ship_id),
            port_id=port_id
        )

    def end_parking(self, port):
        dock_chart = DockChart.objects.get(port=port, end_time=None)
        dock_chart.end_time = timezone.now()
        dock_chart.is_success = False
        dock_chart.save()
        return dock_chart

    def undock_ship(self, ship):
        dock_chart = DockChart.objects.filter(ship=ship, end_time=None).first()
        dock_chart.end_time = timezone.now()
        dock_chart.is_success = True
        dock_chart.save()
        return dock_chart

    def allocate_pirate_port(self, ship):
        pirate_ports = Port.objects.filter(type__ownable=False)
        for pirate_port in pirate_ports:
            if DockChart.objects.filter(port=pirate_port, end_time=None).count() == 0:
                return DockChart.objects.create(ship=ship, port=pirate_port)

    # check pirate port availability
    def is_available(self):
        port_available = False
        pirate_ports = Port.objects.filter(type__ownable=False)
        for pirate_port in pirate_ports:
            if DockChart.objects.filter(port=pirate_port, end_time=None).count() == 0:
                port_available = True
                break

        if port_available:
            return True
        else:
            return False


class DockChart(models.Model):
    start_time = models.DateTimeField(auto_now=True)
    end_time = models.DateTimeField(default=None, null=True)
    is_success = models.BooleanField(default=False)
    ship = models.ForeignKey('Ship', related_name='ships')
    port = models.ForeignKey('Port', related_name='ports')

    objects = DockChartModelManager()

    def __str__(self):
        return self.ship.ship_store.name + " : " + str(self.start_time)


class FineLogModelManager(models.Manager):
    def create_log(self, amount, dock_chart):
        return FineLog.objects.create(amount=amount, dock_chart=dock_chart)


class FineLog(models.Model):
    amount = models.IntegerField()
    dock_chart = models.ForeignKey('DockChart')

    objects = FineLogModelManager()


class Island(models.Model):
    name = models.CharField(max_length=255)
    item = models.ForeignKey('Item')
    # Habitable tells whether the island can be assigned to a user
    habitable = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Level(models.Model):
    level_number = models.IntegerField()
    experience_required = models.IntegerField()

    def __str__(self):
        return str(self.level_number)


class PortTypeModelManager(models.Manager):
    def get_parking_port(self):
        return PortType.objects.get(penalizable=False, ownable=True)

    def get_non_parking_port(self):
        return PortType.objects.get(penalizable=True, ownable=True)


class PortType(models.Model):
    name = models.CharField(max_length=255)
    penalizable = models.BooleanField(default=True)
    ownable = models.BooleanField(default=True)

    objects = PortTypeModelManager()

    def __str__(self):
        return self.name


class PortModelManager(models.Manager):
    def _create_parking_port(self, user):
        return Port.objects.create(user=user, type=PortType.objects.get_parking_port())

    def _create_non_parking_port(self, user):
        return Port.objects.create(user=user, type=PortType.objects.get_non_parking_port())

    def create_initial_ports(self, user):
        """
        Creates parking and non parking ports of a user
        """
        for _ in range(3):
            self._create_parking_port(user=user)

        for _ in range(2):
            self._create_non_parking_port(user=user)

    def get_parking_ports(self, user):
        return Port.objects.filter(user=user, type__ownable=True, type__penalizable=False)

    def get_non_parking_ports(self, user):
        return Port.objects.filter(user=user, type__ownable=True, type__penalizable=True)

    def pirate_port_available(self):
        pirate_ports = Port.objects.filter(type__ownable=False)
        if pirate_ports.count() == 0:
            return False
        return True


# Parking
class Port(models.Model):
    user = models.ForeignKey(User, related_name='user')
    type = models.ForeignKey('PortType', related_name='port')
    log = models.ForeignKey('DockChart', default=None, null=True, related_name='log')

    objects = PortModelManager()

    def is_penalisable(self):
        if self.type.penalizable is False:
            return True
        return False

    def is_idle(self):
        if DockChart.objects.filter(port=self, end_time=None).count() == 0:
            return True
        return False

    def __str__(self):
        return self.user.username + " : " + self.type.name


class RevenueLog(models.Model):
    item_collected = models.IntegerField()
    item = models.ForeignKey('Item')
    dock_chart = models.ForeignKey('DockChart')


class Ship(models.Model):
    ship_store = models.ForeignKey('ShipStore')
    user = models.ForeignKey(User)
    raid_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    upgrade_to = models.ForeignKey("self", default=None, null=True, blank=True)
    upgraded_at = models.DateTimeField(blank=True, null=True)

    def update(self, next_ship_store, user):
        next_ship_instance = Ship.objects.create(ship_store=next_ship_store, user=user)
        self.is_active = False
        self.upgrade_to = next_ship_instance
        self.upgraded_at = timezone.now()
        self.save()

        return next_ship_instance

    def check_inventory(self, user):
        ships = ShipStore.objects.filter(buy_cost__gt=self.ship_store.buy_cost).order_by('buy_cost')
        upgrade_to_ship = ships.exclude(ship=self).first()
        items_required = ShipUpgrade.objects.filter(ship_store=upgrade_to_ship)
        from player.models import Inventory
        user_items = Inventory.objects.filter(user=user)
        for item_required in items_required:
            item_acquired = user_items.get(item=item_required.item_id)
            if item_required.count > item_acquired.count:
                return False
        return True

    def belongs_to(self, user):
        if self.user == user:
            return True
        return False

    def is_idle(self):
        if DockChart.objects.filter(ship=self, end_time=None).count() == 0:
            return True
        return False

    def __str__(self):
        return self.user.username + " : " + self.ship_store.name


class ShipStoreModelManager(models.Manager):
    def buy_raft(self, user):
        raft = ShipStore.objects.order_by('buy_cost').first()
        ship = Ship.objects.create(ship_store=raft, user=user)

        # Decrement user gold

        from player.models import Inventory
        gold = Inventory.objects.filter(user=user, item__name__icontains='Gold').first()
        gold.count -= ship.ship_store.buy_cost
        gold.save()

        ship.save()
        return ship

    def allocate_initial_ship(self, user):
        """
        Assigns initial raft to the user
        """
        raft = ShipStore.objects.order_by('buy_cost').first()
        ship = Ship.objects.create(ship_store=raft, user=user)
        dock = Dock.objects.unlock_first_dock(user=user)
        dock.ship = ship
        dock.save()

        return ship


class ShipStore(models.Model):
    name = models.CharField(max_length=255)
    cost_multiplier = models.FloatField()
    experience_gain = models.IntegerField()
    image = models.ImageField()
    # Buy cost in gold coins
    buy_cost = models.IntegerField()

    objects = ShipStoreModelManager()

    def __str__(self):
        return self.name


class ShipUpgradeModelManager(models.Manager):
    def consume_inventory(self, ship, user):
        ships = ShipStore.objects.filter(buy_cost__gt=ship.ship_store.buy_cost).order_by('buy_cost')
        upgrade_to_shipstore = ships.exclude(ship=ship).first()
        items_required = ShipUpgrade.objects.filter(ship_store=upgrade_to_shipstore)
        from player.models import Inventory
        user_items = Inventory.objects.filter(user=user)
        for item_required in items_required:
            item_acquired = user_items.get(item=item_required.item_id)
            item_acquired.count -= item_required.count
            item_acquired.save()

        return upgrade_to_shipstore


class ShipUpgrade(models.Model):
    ship_store = models.ForeignKey('ShipStore', related_name='items_required', on_delete=models.CASCADE)
    count = models.IntegerField()
    item_id = models.ForeignKey('Item', on_delete=models.CASCADE)
    objects = ShipUpgradeModelManager()

    def __str__(self):
        return self.ship_store.name + " : " + str(self.count) + " " + self.item_id.name

    class Meta:
        unique_together = ('ship_store', 'item_id')


class Slot(models.Model):
    unlock_level = models.ForeignKey('Level')

    def __str__(self):
        return str(self.id) + " : " + str(self.unlock_level)


class Version(models.Model):
    platform = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    is_essential = models.BooleanField(default=False)
