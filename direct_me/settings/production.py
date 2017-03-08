import dj_database_url

from .base import *

ALLOWED_HOSTS = ['direct-me.herokuapp.com']

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_SIGNATURE_VERSION = os.environ.get('AWS_S3_SIGNATURE_VERSION')
AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN')
AWS_S3_FILE_OVERWRITE = False

OPBEAT = {
    'ORGANIZATION_ID': os.environ.get('OPBEAT_ORGANIZATION_ID'),
    'APP_ID': os.environ.get('OPBEAT_APP_ID'),
    'SECRET_TOKEN': os.environ.get('OPBEAT_SECRET_TOKEN'),
}
