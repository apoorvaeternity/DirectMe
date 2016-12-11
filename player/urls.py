from django.conf.urls import url, include
from .views import UserRegistrationView, UserAuthenticationView, UserView, GCMTokenView, UserPasswordUpdateView

urlpatterns = [
    url(r'^register/', UserRegistrationView.as_view()),
    url(r'^gcm/', GCMTokenView.as_view()),
    url(r'^login/', UserAuthenticationView.as_view()),
    url(r'^password-reset/', UserPasswordUpdateView.as_view()),
    url(r'', UserView.as_view()),

]
