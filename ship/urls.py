from django.conf.urls import url

from ship import views

urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^getPorts/(?P<user>[0-9]+)/$',
        views.PortsList.as_view(),
        name='ports'),
    url(r'^getShips/(?P<user>[0-9]+)/$',
        views.ShipsList.as_view(),
        name='ships')
]
