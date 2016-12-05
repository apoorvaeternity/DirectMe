from django.conf.urls import url

from ship import views

urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^getPorts/$',
        views.PortsList.as_view(),
        name='ports'),
    url(r'^getShips/$',
        views.ShipsList.as_view(),
        name='ships')
]
