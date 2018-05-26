# coding=utf-8

import os
import six
import shutil

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from datetime import datetime
from django.core.files import File
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.core.files.storage import Storage
from django.conf import settings
from django.utils.encoding import force_text, force_bytes
from django.utils.deconstruct import deconstructible
from django.utils.timezone import utc
from tempfile import SpooledTemporaryFile

import oss2.utils
import oss2.exceptions
from oss2 import Auth, Service, Bucket, ObjectIterator, BUCKET_ACL_PRIVATE

from .defaults import logger


def _get_config(name, default=None):
    config = os.environ.get(name, getattr(settings, name, default))
    if config is not None:
        if isinstance(config, six.string_types):
            return config.strip()
        else:
            return config
    else:
        raise ImproperlyConfigured("'%s not found in env variables or setting.py" % name)


def _normalize_endpoint(endpoint):
    if not endpoint.startswith('http://') and not endpoint.startswith('https://'):
        return 'https://' + endpoint
    else:
        return endpoint

class OssError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

@deconstructible
class OssStorage(Storage):
    """
    Aliyun OSS Storage
    """

    def __init__(self, access_key_id=None, access_key_secret=None, end_point=None, bucket_name=None, expire_time=None, location='', base_url=''):
        self.access_key_id = access_key_id if access_key_id else _get_config('OSS_ACCESS_KEY_ID')
        self.access_key_secret = access_key_secret if access_key_secret else _get_config('OSS_ACCESS_KEY_SECRET')
        self.end_point = _normalize_endpoint(end_point if end_point else _get_config('OSS_ENDPOINT'))
        self.bucket_name = bucket_name if bucket_name else _get_config('OSS_BUCKET_NAME')
        self.expire_time = expire_time if expire_time else int(_get_config('OSS_EXPIRE_TIME', default=60*60*24*30))

        self.auth = Auth(self.access_key_id, self.access_key_secret)
        self.service = Service(self.auth, self.end_point)
        self.bucket = Bucket(self.auth, self.end_point, self.bucket_name)
        self.location = location
        self.base_url = base_url

        # try to get bucket acl to check bucket exist or not
        try:
            self.bucket_acl = self.bucket.get_bucket_acl().acl
        except oss2.exceptions.NoSuchBucket:
            raise SuspiciousOperation("Bucket '%s' does not exist." % self.bucket_name)

    def _get_key_name(self, name):
        """
        Get the object key name in OSS, e.g.,
        location: /media/
        input   : test.txt
        output  : media/test.txt
        """
        # urljoin won't work if name is absolute path
        name = name.lstrip('/')

        base_path = force_text(self.location)
        final_path = urljoin(base_path + "/", name)
        name = os.path.normpath(final_path.lstrip('/'))

        # Add / to the end of path since os.path.normpath will remove it
        if final_path.endswith('/') and not name.endswith('/'):
            name += '/'

        if six.PY2:
            name = name.encode('utf-8')
        return name

    def _open(self, name, mode='rb'):
        logger().debug("name: %s, mode: %s", name, mode)
        if mode != "rb":
            raise ValueError("OSS files can only be opened in read-only mode")

        target_name = self._get_key_name(name)
        logger().debug("target name: %s", target_name)
        try:
            # Load the key into a temporary file
            tmpf = SpooledTemporaryFile(max_size=10*1024*1024)  # 10MB
            obj = self.bucket.get_object(target_name)
            logger().info("content length: %d, requestid: %s", obj.content_length, obj.request_id)
            if obj.content_length is None:
                shutil.copyfileobj(obj, tmpf)
            else:
                oss2.utils.copyfileobj_and_verify(obj, tmpf, obj.content_length, request_id=obj.request_id)
            tmpf.seek(0)
            return OssFile(tmpf, target_name, self)
        except oss2.exceptions.NoSuchKey:
            raise OssError("%s does not exist" % name)
        except:
            raise OssError("Failed to open %s" % name)

    def _save(self, name, content):
        target_name = self._get_key_name(name)
        logger().debug("target name: %s", target_name)
        logger().debug("content: %s", content)
        self.bucket.put_object(target_name, content)
        return os.path.normpath(name)

    def create_dir(self, dirname):
        target_name = self._get_key_name(dirname)
        if not target_name.endswith('/'):
            target_name += '/'

        self.bucket.put_object(target_name, '')

    def exists(self, name):
        target_name = self._get_key_name(name)
        logger().debug("name: %s, target name: %s", name, target_name)
        if name.endswith("/"):
            # This looks like a directory, but OSS has no concept of directories
            # need to check whether the key starts with this prefix
            result = self.bucket.list_objects(prefix=target_name, delimiter='', marker='', max_keys=1)
            if len(result.object_list) == 0:
                logger().debug("object list: %s", result.object_list)
            else:
                logger().debug("object list: %s", result.object_list[0].key)
            return bool(result.object_list)

        exist = self.bucket.object_exists(target_name)
        logger().debug("'%s' exist: %s", target_name, exist)
        if not exist:
            # It's not a file, but it might be a directory. Check again that it's not a directory.
            name2 = name + "/"
            logger().debug("to check %s", name2)
            return self.exists(name2)

        return exist

    def get_file_meta(self, name):
        name = self._get_key_name(name)
        return self.bucket.get_object_meta(name)

    def size(self, name):
        file_meta = self.get_file_meta(name)
        return file_meta.content_length

    def modified_time(self, name):
        file_meta = self.get_file_meta(name)
        return datetime.fromtimestamp(file_meta.last_modified)

    created_time = accessed_time = modified_time

    def get_modified_time(self, name):
        file_meta = self.get_file_meta(name)

        if settings.USE_TZ:
            return datetime.utcfromtimestamp(file_meta.last_modified).replace(tzinfo=utc)
        else:
            return datetime.fromtimestamp(file_meta.last_modified)

    get_created_time = get_accessed_time = get_modified_time

    def content_type(self, name):
        name = self._get_key_name(name)
        file_info = self.bucket.head_object(name)
        return file_info.content_type

    def listdir(self, name):
        if name == ".":
            name = ""
        name = self._get_key_name(name)
        if not name.endswith('/'):
            name += "/"
        logger().debug("name: %s", name)

        files = []
        dirs = []

        for obj in ObjectIterator(self.bucket, prefix=name, delimiter='/'):
            if obj.is_prefix():
                dirs.append(obj.key)
            else:
                files.append(obj.key)

        logger().debug("dirs: %s", list(dirs))
        logger().debug("files: %s", files)
        return dirs, files

    def url(self, name):
        key = self._get_key_name(name)

        # Return signed bucket url for private acl.
        if self.bucket_acl == BUCKET_ACL_PRIVATE:
            return self.bucket.sign_url('GET', key, expires=self.expire_time)

        # For public or public-read acl bucket, use base_url is possible,
        # otherwise fallback to public bucket url.
        if self.base_url.startswith("http"):
            return urljoin(self.base_url, key)
        else:
            scheme, endpoint = self.end_point.split('//')
            return urljoin(scheme + '//' + self.bucket_name + '.' + endpoint, key)

    def delete(self, name):
        name = self._get_key_name(name)
        logger().debug("delete name: %s", name)
        result = self.bucket.delete_object(name)

    def delete_with_slash(self, dirname):
        name = self._get_key_name(dirname)
        if not name.endswith('/'):
            name += '/'
        logger().debug("delete name: %s", name)
        result = self.bucket.delete_object(name)

class OssMediaStorage(OssStorage):
    def __init__(self):
        fallback_location = settings.MEDIA_URL
        if fallback_location.startswith('http'):
            fallback_location = '/media/'
        super(OssMediaStorage, self).__init__(
            location=getattr(settings, 'OSS_MEDIA_LOCATION', fallback_location),
            base_url=settings.MEDIA_URL)

    def save(self, name, content, max_length=None):
        return super(OssMediaStorage, self)._save(name, content)


class OssStaticStorage(OssStorage):
    def __init__(self):
        fallback_location = settings.STATIC_URL
        if fallback_location.startswith('http'):
            fallback_location = '/static/'
        super(OssStaticStorage, self).__init__(
            location=getattr(settings, 'OSS_STATIC_LOCATION', fallback_location),
            base_url=settings.STATIC_URL
        )

    def save(self, name, content, max_length=None):
        return super(OssStaticStorage, self)._save(name, content)

class OssFile(File):
    """
    A file returned from AliCloud OSS
    """

    def __init__(self, content, name, storage):
        super(OssFile, self).__init__(content, name)
        self._storage = storage

    def open(self, mode="rb"):
        if self.closed:
            self.file = self._storage.open(self.name, mode).file
        return super(OssFile, self).open(mode)
