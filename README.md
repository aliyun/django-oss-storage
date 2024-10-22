# Django AliCloud OSS Storage V2

**django-oss-storage-v2** provides a Django AliCloud OSS file storage,
compatible with Django 5.1+.

## Features

-   Django file storage for AliCloud OSS
-   Django static file storage for AliCloud OSS
-   Works in Python 2 & 3
-   Supports Django 5.1+

## Installation

``` bash
$ pip install django-oss-storage-v2
```

## for Django < 5.1

-   Add `'django_oss_storage'` to your `INSTALLED_APPS` setting
-   Set your `DEFAULT_FILE_STORAGE` setting to
    `"django_oss_storage.backends.OssMediaStorage"`
-   Set your `STATICFILES_STORAGE` setting to
    `"django_oss_storage.backends.OssStaticStorage"`
-   Configure your AliCloud OSS settings (Refer below).

### Storage settings

Use the following settings for file storage.

``` bash
STATICFILES_STORAGE = 'django_oss_storage.backends.OssStaticStorage'

DEFAULT_FILE_STORAGE = 'django_oss_storage.backends.OssMediaStorage'
```

### Authentication settings

Use the following settings to authenticate with AliCloud OSS.

``` bash
# AliCloud access key ID
OSS_ACCESS_KEY_ID = <Your Access Key ID>

# AliCloud access key secret
OSS_ACCESS_KEY_SECRET = <Your Access Key Secret>
```

### OSS settings

For public or public-read buckets, storage urls will be
bucket_name.endpoint/key format

For private buckets, storage urls will be signed url. The expires time
can be set by OSS_EXPIRE_TIME as environment variable or as Django
settings. The default value for OSS_EXPIRE_TIME is 30 days.

``` bash
OSS_EXPIRE_TIME = <Expire Time in Seconds>

# The name of the bucket to store files in
OSS_BUCKET_NAME = <Your bucket name>

# The URL of AliCloud OSS endpoint
# Refer https://www.alibabacloud.com/help/zh/doc-detail/31837.htm for OSS Region & Endpoint
OSS_ENDPOINT = <Your access endpoint>

```

## for Django >= 5.1

-   Add `'django_oss_storage'` to your `INSTALLED_APPS` setting
-   Set your `STORAGE` setting as below.

``` bash
STORAGES = {
    "default": {
        "BACKEND": "django_oss_storage.backends.OssMediaStorage",
        "OPTIONS": {
            "access_key_id": <Your Access Key ID>,
            "access_key_secret": <Your Access Key Secret>,
            "bucket_name": <Your bucket name>,
            "endpoint": <Your access endpoint>,
            "expire_time": <Expire Time in Seconds>,
        }
    },
    "staticfiles": {
        "BACKEND": "django_oss_storage.backends.OssStaticStorage",
        "OPTIONS": {
            "access_key_id": <Your Access Key ID>,
            "access_key_secret": <Your Access Key Secret>,
            "bucket_name": <Your bucket name>,
            "endpoint": <Your access endpoint>,
            "expire_time": <Expire Time in Seconds>,
        }
    }
}
```


## File storage settings

Use the following settings to configure AliCloud OSS file storage.

``` bash
# The default location for your project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The default location for your media files
# In both cases, your media files will be put into OSS://<your_bucket>/media/
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_ROOT = "/media/"

# Your can use this MEDIA_URL in your django templates
MEDIA_URL = "http://<your-bucket>.<your-endpoint>.aliyuncs.com/media/"
# Or your custom domain MEDIA_URL
MEDIA_URL = "http://<your-custom-domain>/media/"
```

## Staticfiles storage settings

All of the file storage settings are available for the staticfiles
storage.

``` bash
# The default location for your static files
# In both case, your static files will be put into OSS://<your_bucket>/static/
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = "/static/"

# Your can use this STATIC_URL in your django templates
STATIC_URL = 'http://<your-bucket>.<your-endpoint>.aliyuncs.com/static/'
# Or your custom domain STATIC_URL
STATIC_URL = "http://<your-custom-domain>/static/"
```

staticfiles provides command \'collectstatic\'. Run following command to
collect all sub-folder \'static\' of each app and upload to STATIC_URL.

``` bash
$ python manage.py collectstatic
```

## Testing

First set the required AccessKeyId, AccessKeySecret, endpoint and bucket
information for the test through environment variables (**Do not use the
bucket for the production environment**). Take the Linux system for
example:

``` bash
$ export OSS_ACCESS_KEY_ID=<AccessKeyId>
$ export OSS_ACCESS_KEY_SECRET=<AccessKeySecret>
$ export OSS_BUCKET_NAME=<bucket>
$ export OSS_ENDPOINT=<endpoint>
```

## Support and announcements

Downloads and bug tracking can be found at the [main project
website](http://github.com/twisker/django-oss-storage).

## License

-   [MIT](https://github.com/twisker/django-oss-storage/blob/master/LICENSE).
