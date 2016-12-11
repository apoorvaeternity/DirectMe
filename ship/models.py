from django.contrib.auth.models import User
from django.db import models

from core.models import Slot, Item, ShipStore


class Ship(models.Model):
    ship_store = models.ForeignKey(ShipStore)
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


class PortType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Parking
class Port(models.Model):
    user = models.ForeignKey(User, related_name='user')
    type = models.ForeignKey(PortType, related_name='port')
    log = models.ForeignKey('DockChart', default=None, null=True, related_name='log')

    def __str__(self):
        return self.user.username + " : " + self.type.name


# Garage
class Dock(models.Model):
    user = models.ForeignKey(User)
    slot = models.ForeignKey(Slot)
    ship = models.ForeignKey(Ship, default=None, null=True)


class DockChart(models.Model):
    start_time = models.DateTimeField(auto_now=True)
    end_time = models.DateTimeField(default=None, null=True)
    is_success = models.BooleanField(default=False)
    ship = models.ForeignKey(Ship, related_name='ships')
    port = models.ForeignKey(Port, related_name='ports')


class FineLog(models.Model):
    amount = models.IntegerField()
    dock_chart = models.ForeignKey(DockChart)


class RevenueLog(models.Model):
    item_collected = models.IntegerField()
    item = models.ForeignKey(Item)
    dock_chart = models.ForeignKey(DockChart)
