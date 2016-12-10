from django.contrib import admin

from .models import ShipStore, Level, ShipUpgrade, Item, Island, Slot, Version


class ShipStoreModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'experience_gain', 'cost_multiplier', 'buy_cost')


class LevelModelAdmin(admin.ModelAdmin):
    list_display = ('level_number', 'experience_required')


class ShipUpgardeModelAdmin(admin.ModelAdmin):
    list_display = ('ship_store', 'count', 'item_id')


class SlotModelAdmin(admin.ModelAdmin):
    list_display = ('unlock_level', 'id')


class VersionModelAdmin(admin.ModelAdmin):
    list_display = ('platform', 'version', 'is_essential')

admin.site.register(ShipStore, ShipStoreModelAdmin)
admin.site.register(Level, LevelModelAdmin)
admin.site.register(ShipUpgrade, ShipUpgardeModelAdmin)
admin.site.register(Item)
admin.site.register(Island)
admin.site.register(Slot, SlotModelAdmin)
admin.site.register(Version, VersionModelAdmin)