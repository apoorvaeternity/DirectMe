from django.conf.urls import url

from core import views

urlpatterns = [
    url(r'^ships/$', views.ShipsList.as_view(), name='ship-list'),
    url(r'^ship/(?P<ship_id>[0-9]+)/$', views.ShipsDetail.as_view(), name='ship-detail'),
]
