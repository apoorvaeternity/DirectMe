from django.db import models


class ShipStore(models.Model):
    name = models.CharField(max_length=255)
    cost_multiplier = models.FloatField()
    experience_gain = models.IntegerField()
    image = models.ImageField()
    # Buy cost in gold coins
    buy_cost = models.IntegerField()

    def __str__(self):
        return self.name


class Level(models.Model):
    level_number = models.IntegerField()
    experience_required = models.IntegerField()

    def __str__(self):
        return str(self.level_number)


class Item(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ShipUpgrade(models.Model):
    ship_store = models.ForeignKey(ShipStore)
    count = models.IntegerField()
    item_required = models.OneToOneField(Item)

    def __str__(self):
        return self.ship_store.name + " " + self.item_required.name


class Island(models.Model):
    name = models.CharField(max_length=255)
    item = models.ForeignKey(Item)

    def __str__(self):
        return self.name


class PortType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
