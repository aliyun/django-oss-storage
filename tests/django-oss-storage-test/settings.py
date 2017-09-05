import os
import sys
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(BASE_DIR))

SECRET_KEY = "test"

USE_TZ = True
TIME_ZONE = 'UTC'

# OSS settings
OSS_ACCESS_KEY_ID = os.environ.get("OSS_ACCESS_KEY_ID")
OSS_ACCESS_KEY_SECRET = os.environ.get("OSS_ACCESS_KEY_SECRET")
OSS_BUCKET_NAME = os.environ.get("OSS_BUCKET_NAME")
OSS_BUCKET_ACL = os.environ.get("OSS_BUCKET_ACL")

OSS_ENDPOINT = os.environ.get("OSS_ENDPOINT")

OSS_PREFIX = 'oss://'
MEDIA_PREFIX = 'media/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
ADMIN_MEDIA_PREFIX = '/static/admin'

STATIC_PREFIX = 'static/'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEFAULT_FILE_STORAGE = 'django_oss_storage.backends.OssMediaStorage'
STATICFILES_STORAGE = 'django_oss_storage.backends.OssStaticStorage'

# Application definition

INSTALLED_APPS = (
    "django.contrib.staticfiles",
    "django_oss_storage",
)


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
