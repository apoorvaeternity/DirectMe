from django.conf.urls import url

from core.views import ShipsListView
from .views import UserRegistrationView, UserAuthenticationView, UserView, GCMTokenView, UserPasswordUpdateView, \
    SuggestionListView, UsernameSearchView, EmailSearchView, EmailVerificationView, exchange_token

urlpatterns = [
    url(r'social/(?P<backend>[^/]+)/$', exchange_token, name='google-login'),
    url(r'^email-verification/(?P<get_token>[^/]+)/$', EmailVerificationView.as_view(), name='email-verification'),
    url(r'^search-username/(?P<username>\w+)/$', UsernameSearchView.as_view(), name='search-username'),
    url(r'^search-email/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', EmailSearchView.as_view(),
        name='search-email'),
    url(r'^register/', UserRegistrationView.as_view(), name='register'),
    url(r'^gcm/', GCMTokenView.as_view(), name='gcm'),
    url(r'^login/', UserAuthenticationView.as_view(), name='login'),
    url(r'^password-reset/', UserPasswordUpdateView.as_view(), name='reset-password'),
    url(r'^ships/$', ShipsListView.as_view(), name='ships'),
    url(r'^get-suggestions/$', SuggestionListView.as_view(), name='suggestions'),
    url(r'', UserView.as_view(), name='user'),
]
