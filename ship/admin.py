from django.contrib import admin

from .models import Ship, Port, Dock, DockChart, FineLog, RevenueLog, PortType


class DockChartModelAdmin(admin.ModelAdmin):
    list_display = ('ship', 'port', 'start_time', 'end_time', 'is_success')

admin.site.register(Ship)
admin.site.register(Port)
admin.site.register(PortType)
admin.site.register(Dock)
admin.site.register(DockChart,DockChartModelAdmin)
admin.site.register(FineLog)
admin.site.register(RevenueLog)
