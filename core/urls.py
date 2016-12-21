from django.conf.urls import url

from core import views

urlpatterns = [
    url(r'^ships/$', views.ShipsList.as_view(), name='ship-list'),
    url(r'^ship/(?P<ship_id>[0-9]+)/$', views.ShipsDetail.as_view(), name='ship-detail'),
    url(r'^version/$', views.VersionCheck.as_view()),

    url(r'^ports/$', views.PortsListView.as_view(), name='ports'),
    url(r'^ships/$', views.ShipsListView.as_view(), name='ships'),
    url(r'^docks/$', views.DocksListView.as_view(), name='docks'),
    url(r'^fine/$', views.FineView.as_view(), name='fine'),
    url(r'^undock/$', views.UndockShipView.as_view(), name='undock'),
    url(r'^dock/$', views.DockShipView.as_view(), name='dock-ship'),
    url(r'^update-ship/$', views.UpdateShipView.as_view(), name='update-ship'),
]
