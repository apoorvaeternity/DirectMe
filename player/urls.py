from django.conf.urls import url, include
from .views import UserRegistrationView, UserAuthenticationView, User, GCMTokenView, UserPasswordUpdateView

urlpatterns = [
    url(r'^register/', UserRegistrationView.as_view()),
    url(r'^gcm/', GCMTokenView.as_view()),
    url(r'^login/', UserAuthenticationView.as_view()),
    url(r'^password-reset/', UserPasswordUpdateView.as_view()),
    url(r'', User.as_view()),

]
