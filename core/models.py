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
    ship_store = models.ForeignKey(ShipStore, related_name='items_required', on_delete=models.CASCADE)
    count = models.IntegerField()
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.ship_store.name + " : " + str(self.count) + " " + self.item_id.name

    class Meta:
        unique_together = ('ship_store', 'item_id')


class Island(models.Model):
    name = models.CharField(max_length=255)
    item = models.ForeignKey(Item)

    def __str__(self):
        return self.name


class Slot(models.Model):
    unlock_level = models.ForeignKey(Level)

    def __str__(self):
        return str(self.id) + " : " + str(self.unlock_level)
