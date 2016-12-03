from django.contrib import admin

from .models import ShipStore, Level, ShipUpgrade, Item, PortType, Island

admin.site.register(ShipStore)
admin.site.register(Level)
admin.site.register(ShipUpgrade)
admin.site.register(Item)
admin.site.register(PortType)
admin.site.register(Island)