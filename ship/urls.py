from django.conf.urls import url

from ship import views

urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^getPorts/(?P<pk>[0-9]+)/$',
        views.PortsList.as_view(),
        name='ports'),
]
