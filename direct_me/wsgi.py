"""
WSGI config for direct_me project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

if 'IS_HEROKU' in os.environ:
    from whitenoise.django import DjangoWhiteNoise

    application = get_wsgi_application()
    application = DjangoWhiteNoise(application)

else:

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "direct_me.settings")
    application = get_wsgi_application()
