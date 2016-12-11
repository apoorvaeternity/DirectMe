from django.conf.urls import url

from ship import views

urlpatterns = [
    url(r'^ports/$', views.PortsListView.as_view(), name='ports'),
    url(r'^ships/$', views.ShipsListView.as_view(), name='ships'),
    url(r'^docks/$', views.DocksListView.as_view(), name='docks'),
    url(r'^fine/(?P<port_id>[0-9]+)/$', views.FineView.as_view(), name='fine'),
    url(r'^undock/(?P<ship_id>[0-9]+)/$', views.UndockShipView.as_view(), name='undock'),
    url(r'^dock/$', views.DockShipView.as_view(), name='dock-ship'),

]
