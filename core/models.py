from django.contrib.auth.models import User
from django.db import models


class DockModelManager(models.Manager):
    def create_initial_docks(self, user):
        for slot in Slot.objects.all():
            Dock.objects.create(user=user, slot=slot)

    def unlock_first_dock(self, user):
        return Dock.objects.filter(user=user).order_by('slot__unlock_level').first()


# Garage
class Dock(models.Model):
    user = models.ForeignKey(User)
    slot = models.ForeignKey('Slot')
    ship = models.ForeignKey('Ship', default=None, null=True)

    objects = DockModelManager()


class DockChart(models.Model):
    start_time = models.DateTimeField(auto_now=True)
    end_time = models.DateTimeField(default=None, null=True)
    is_success = models.BooleanField(default=False)
    ship = models.ForeignKey('Ship', related_name='ships')
    port = models.ForeignKey('Port', related_name='ports')

    def __str__(self):
        return self.ship.ship_store.name + " : " + str(self.start_time)


class FineLog(models.Model):
    amount = models.IntegerField()
    dock_chart = models.ForeignKey('DockChart')


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
        for _ in range(2):
            self._create_parking_port(user=user)

        for _ in range(3):
            self._create_non_parking_port(user=user)


# Parking
class Port(models.Model):
    user = models.ForeignKey(User, related_name='user')
    type = models.ForeignKey('PortType', related_name='port')
    log = models.ForeignKey('DockChart', default=None, null=True, related_name='log')

    objects = PortModelManager()

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
    def allocate_initial_ship(self, user):
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


class ShipUpgrade(models.Model):
    ship_store = models.ForeignKey('ShipStore', related_name='items_required', on_delete=models.CASCADE)
    count = models.IntegerField()
    item_id = models.ForeignKey('Item', on_delete=models.CASCADE)

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
