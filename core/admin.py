from django.contrib import admin

from .models import ShipStore, Level, ShipUpgrade, Item, Island, Slot, Version, Ship, Port, Dock, DockChart, FineLog, \
    RevenueLog, PortType


class ShipStoreModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'ship_id', 'experience_gain', 'cost_multiplier', 'buy_cost')


class LevelModelAdmin(admin.ModelAdmin):
    list_display = ('level_number', 'experience_required')


class ShipUpgardeModelAdmin(admin.ModelAdmin):
    list_display = ('ship_store', 'count', 'item_id')


class SlotModelAdmin(admin.ModelAdmin):
    list_display = ('unlock_level', 'id')


class VersionModelAdmin(admin.ModelAdmin):
    list_display = ('platform', 'version', 'is_essential')


class DockChartModelAdmin(admin.ModelAdmin):
    list_display = ('ship', 'port', 'start_time', 'end_time', 'is_success')


class PortModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'log')


admin.site.register(ShipStore, ShipStoreModelAdmin)
admin.site.register(Level, LevelModelAdmin)
admin.site.register(ShipUpgrade, ShipUpgardeModelAdmin)
admin.site.register(Item)
admin.site.register(Island)
admin.site.register(Slot, SlotModelAdmin)
admin.site.register(Version, VersionModelAdmin)

admin.site.register(Ship)
admin.site.register(Port, PortModelAdmin)
admin.site.register(PortType)
admin.site.register(Dock)
admin.site.register(DockChart, DockChartModelAdmin)
admin.site.register(FineLog)
admin.site.register(RevenueLog)
