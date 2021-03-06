"""direct_me URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import os

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^user/', include('player.urls')),
    url(r'^core/', include('core.urls')),
    url(r'^docs/', include('rest_framework_docs.urls')),
    url('', include('social_django.urls', namespace='social'))
]

if 'SECRET_KEY' not in os.environ:  # Uses SECRET_KEY environment variable to check whether project is under production.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
