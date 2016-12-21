from django.conf.urls import url

from core.views import ShipsListView
from .views import UserRegistrationView, UserAuthenticationView, UserView, GCMTokenView, UserPasswordUpdateView

urlpatterns = [
    url(r'^register/', UserRegistrationView.as_view(), name='register'),
    url(r'^gcm/', GCMTokenView.as_view(), name='gcm'),
    url(r'^login/', UserAuthenticationView.as_view(), name='login'),
    url(r'^password-reset/', UserPasswordUpdateView.as_view(), name='reset-password'),
    url(r'^ships/$', ShipsListView.as_view(), name='ships'),
    url(r'', UserView.as_view(), name='user'),

]
