from django.conf.urls import url, include
from .views import UserRegistrationView, UserAuthenticationView, User

urlpatterns = [
    url(r'^register/', UserRegistrationView.as_view()),
    url(r'^login/', UserAuthenticationView.as_view()),
    url(r'', User.as_view()),
]
