from django.contrib import admin

from .models import ShipStore, Level, ShipUpgrade, Item, Island

admin.site.register(ShipStore)
admin.site.register(Level)
admin.site.register(ShipUpgrade)
admin.site.register(Item)
admin.site.register(Island)
