Django AliCloud OSS Storage
===========================

**django-oss-storage** provides a Django AliCloud OSS file storage.


Features
========

- Django file storage for AliCloud OSS
- Django static file storage for AliCloud OSS
- Serving file via AliCloud CDN
- Works in Python 2 & 3

Installation
============

* Install

.. code-block:: bash

    $ pip install django-oss-storage

- Add ``'django_oss_storage'`` to your ``INSTALLED_APPS`` setting
- Set your ``DEFAULT_FILE_STORAGE`` setting to ``"django_oss_storage.backends.OssMediaStorage"``
- Set your ``STATICFILES_STORAGE`` setting to ``"django_oss_storage.backends.OssStaticStorage"``
- Configure your AliCloud OSS settings (Refer below).

Use the following settings for file storage.

.. code-block:: bash

    STATICFILES_STORAGE = 'django_oss_storage.backends.OssStaticStorage'

    DEFAULT_FILE_STORAGE = 'django_oss_storage.backends.OssMediaStorage'

Authentication settings
=======================

Use the following settings to authenticate with AliCloud OSS.

.. code-block:: bash

    # AliCloud access key ID
    OSS_ACCESS_KEY_ID = <Your Access Key ID>

    # AliCloud access key secret
    OSS_ACCESS_KEY_SECRET = <Your Access Key Secret>

OSS storage settings
====================

Use the following settings to configure AliCloud OSS file storage.

.. code-block:: bash

    # The name of the bucket to store files in
    OSS_BUCKET_NAME = <Your bucket name>

    # The URL of AliCloud OSS endpoint
    # Refer https://www.alibabacloud.com/help/zh/doc-detail/31837.htm for OSS Region & Endpoint
    OSS_ENDPOINT = <Your access endpoint>

    # The expire time to construct signed url for private acl bucket.
    # Can be set by OSS_EXPIRE_TIME as environment variable or as Django
    # settings. The default value is 30 days.
    OSS_EXPIRE_TIME = <Expire Time in Seconds>

OSS media storage settings
==========================

All of the OSS storage settings are available for the media storage.

.. code-block:: bash

    # The default location for the media files stored in bucket.
    OSS_MEDIA_LOCATION = '/media/'

    # URL that handles the media served. It only works for public or
    # public-read acl bucket (i.e. put AliCloud OSS behind CDN).
    # If value not starts with 'http', storage urls will fallback to
    # default OSS url which is bucket_name.endpoint/key format.
    # For private acl, storage urls will be the signed url.
    MEDIA_URL = 'https://media.example.com/'

OSS static storage storage settings
===================================

All of the OSS storage settings are available for the media storage.

.. code-block:: bash

    # The default location for the static files stored in bucket.
    OSS_STATIC_LOCATION = '/static/'

    # URL that handles the static file served. It only works for public or
    # public-read acl bucket (i.e. put AliCloud OSS behind CDN).
    # If value not starts with 'http', storage urls will fallback to
    # default OSS url which is bucket_name.endpoint/key format.
    # For private acl, storage urls will be the signed url.
    STATIC_URL = 'https://static.example.com/'

staticfiles provides command 'collectstatic'. Run following command to collect all sub-folder 'static' of each app
and upload to OSS_STATIC_LOCATION.

.. code-block:: bash

    $ python manage.py collectstatic


Testing
=======

First set the required AccessKeyId, AccessKeySecret, endpoint and bucket information for the test through environment variables (**Do not use the bucket for the production environment**).
Take the Linux system for example:

.. code-block:: bash

    $ export OSS_ACCESS_KEY_ID=<AccessKeyId>
    $ export OSS_ACCESS_KEY_SECRET=<AccessKeySecret>
    $ export OSS_BUCKET_NAME=<bucket>
    $ export OSS_ENDPOINT=<endpoint>

Support and announcements
=========================

Downloads and bug tracking can be found at the `main project website <http://github.com/aliyun/django-oss-storage>`_.

License
=======

- `MIT <https://github.com/aliyun/django-oss-storage/blob/master/LICENSE>`_.
