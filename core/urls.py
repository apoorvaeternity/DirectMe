from django.conf.urls import url

from core import views

urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^getAll/$',
        views.ShipsList.as_view(),
        name='ship-list'),
]
