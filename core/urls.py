from django.conf.urls import url

from core import views

urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^getAllShips/$',
        views.ShipsList.as_view(),
        name='ship-list'),
    url(r'^getShipDetails/(?P<pk>[0-9]+)/$',
        views.ShipsDetail.as_view(),
        name='ship-detail'),
]
