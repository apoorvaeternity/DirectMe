from django.db import models
from django.contrib.auth.models import User

from core.models import Slot, Item, ShipStore


class Ship(models.Model):
    ship_store = models.ForeignKey(ShipStore)
    user = models.ForeignKey(User)
    raid_count = models.IntegerField()
    is_active = models.BooleanField()
    upgrade_to = models.ForeignKey("self", default=None, null=True)
    upgraded_at = models.DateTimeField()


class PortType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Port(models.Model):
    user = models.ForeignKey(User)
    type = models.ForeignKey(PortType)

    def __str__(self):
        return self.user.username


class Dock(models.Model):
    user = models.ForeignKey(User)
    slot = models.ForeignKey(Slot)
    ship = models.ForeignKey(Ship)

    def __str__(self):
        return self.user.username


class DockChart(models.Model):
    start_time = models.DateTimeField(auto_now=True)
    end_time = models.DateTimeField()
    is_success = models.BooleanField()
    ship = models.ForeignKey(Ship)
    port = models.ForeignKey(Port)


class FineLog(models.Model):
    amount = models.IntegerField()
    dock_chart = models.ForeignKey(DockChart)


class RevenueLog(models.Model):
    item_collected = models.IntegerField()
    item = models.ForeignKey(Item)
    dock_chart = models.ForeignKey(DockChart)
