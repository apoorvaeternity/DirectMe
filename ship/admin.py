from django.contrib import admin

from .models import Ship, Port, Dock, DockChart, FineLog, RevenueLog

admin.site.register(Ship)
admin.site.register(Port)
admin.site.register(Dock)
admin.site.register(DockChart)
admin.site.register(FineLog)
admin.site.register(RevenueLog)
