from django.conf.urls import url

from ship import views

urlpatterns = [
    url(r'^ports/$', views.PortsList.as_view(), name='ports'),
    url(r'^ships/$', views.ShipsList.as_view(), name='ships'),
    url(r'^docks/$', views.DocksList.as_view(), name='docks')
]
