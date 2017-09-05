# -*- coding: utf-8 -*-

import os 
import logging
import requests
from datetime import timedelta
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from django.conf import settings
from django.test import SimpleTestCase
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils import timezone
from django.utils.timezone import is_naive, make_naive, utc
from django_oss_storage.backends import OssError, OssMediaStorage, OssStaticStorage
from django_oss_storage import defaults
from oss2 import to_unicode

logger = logging.getLogger('')
logger.setLevel(logging.INFO)
logfile = os.path.join(os.getcwd(), 'test.log')
fh = RotatingFileHandler(logfile, mode='a', maxBytes=50 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter("%(asctime)s %(levelname)-8s[%(filename)s:%(lineno)d(%(funcName)s)] %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

class TestOssStorage(SimpleTestCase):

    @contextmanager
    def save_file(self, name="test.txt", content=b"test", storage=default_storage):
        logging.info("name: %s", name)
        logging.debug("content: %s", content)
        name = storage.save(name, content)
        try:
            yield name
        finally:
            storage.delete(name)
            pass

    @contextmanager
    def create_dir(self, name="testdir/", storage=default_storage):
        logging.info("name: %s", name)
        name = storage.create_dir(name)
        try:
            yield name
        finally:
            pass

    def test_settings_mported(self):
        # Make sure bucket 'test-tmp-b1' exist under your OSS account
        self.assertEqual(settings.OSS_BUCKET_NAME, "test-tmp-b1")
        with self.settings(OSS_BUCKET_NAME="test"):
            self.assertEqual(settings.OSS_BUCKET_NAME, "test")
        self.assertEqual(settings.OSS_BUCKET_NAME, "test-tmp-b1")

    def test_open_missing(self):
        self.assertFalse(default_storage.exists("test.txt"))
        self.assertRaises(OssError, lambda: default_storage.open("test.txt"))

    def test_open_writeMode(self):
        self.assertFalse(default_storage.exists("test.txt"))
        with self.save_file(name="test.txt"):
            self.assertTrue(default_storage.exists("test.txt"))
            self.assertRaises(ValueError, lambda: default_storage.open("test.txt", "wb"))

    def test_save_and_open(self):
        with self.save_file() as name:
            self.assertEqual(name, "test.txt")
            handle = default_storage.open(name)
            logging.info("handle: %s", handle)
            self.assertEqual(str(handle.read()), b"test")

    def test_save_and_open_cn(self):
        with self.save_file(content=u'我的座右铭') as name:
            self.assertEqual(name, "test.txt")
            handle = default_storage.open(name)
            logging.info("handle: %s", handle)
            self.assertEqual(handle.read(), '我的座右铭')

    def test_save_text_mode(self):
        with self.save_file(content="test"):
            self.assertEqual(default_storage.open("test.txt").read(), b"test")
            self.assertEqual(default_storage.content_type("test.txt"), b"text/plain")

    def test_save_small_file(self):
        with self.save_file():
            logging.info("content type: %s", default_storage.content_type("test.txt"))
            self.assertEqual(default_storage.open("test.txt").read(), b"test")
            self.assertEqual(requests.get(default_storage.url("test.txt", 60)).content, b"test")

    def test_save_big_file(self):
        with self.save_file(content=b"test" * 1000):
            logging.info("content type: %s", default_storage.content_type("test.txt"))
            self.assertEqual(default_storage.open("test.txt").read(), b"test" * 1000)
            self.assertEqual(requests.get(default_storage.url("test.txt", 60)).content, b"test" * 1000)

    def test_url(self):
        with self.save_file():
            url = default_storage.url("test.txt", 100)
            logging.info("url: %s", url)
            response = requests.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"test")
            self.assertEqual(response.headers['Content-Type'], b"text/plain")

    def test_url_cn(self):
        objname = to_unicode("本地文件名.txt")
        logging.info("objname: %s", objname)
        with self.save_file(objname, content=u'我的座右铭') as name:
            self.assertEqual(name, objname)
            url = default_storage.url(objname, 300)
            logging.info("url: %s", url)
            response = requests.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, '我的座右铭')
            self.assertEqual(response.headers['Content-Type'], b"text/plain")

    def test_exists(self):
        self.assertFalse(default_storage.exists("test.txt"))
        with self.save_file():
            self.assertTrue(default_storage.exists("test.txt"))
            self.assertFalse(default_storage.exists("fo"))

    def test_exists_long_path(self):
        self.assertFalse(default_storage.exists("admin/img/sorting-icons.svg"))
        with self.save_file("admin/img/sorting-icons.svg"):
            self.assertTrue(default_storage.exists("admin/img/sorting-icons.svg"))

    def test_create_dir(self):
        self.assertFalse(default_storage.exists("test3"))
        with self.create_dir('test3/'):
            self.assertTrue(default_storage.exists("test3"))
            self.assertTrue(default_storage.exists("test3/"))
        default_storage.delete_with_slash("test3/")
        self.assertFalse(default_storage.exists("test3/"))

    def test_exists_dir(self):
        self.assertFalse(default_storage.exists("test"))
        self.assertFalse(default_storage.exists("test/"))
        with self.save_file(name="test/bar.txt"):
            self.assertTrue(default_storage.exists("test"))
            self.assertTrue(default_storage.exists("test/"))

    def test_size(self):
        with self.save_file():
            self.assertEqual(default_storage.size("test.txt"), 4)

    def test_delete(self):
        with self.save_file():
            self.assertTrue(default_storage.exists("test.txt"))
            default_storage.delete("test.txt")
        self.assertFalse(default_storage.exists("test.txt"))

    def test_modified_time(self):
        with self.save_file():
            modified_time = default_storage.modified_time("test.txt")
            logging.info("modified time: %s", modified_time)
            self.assertTrue(is_naive(modified_time))
            self.assertLess(abs(modified_time - make_naive(timezone.now(), utc)), timedelta(seconds=10))
            self.assertEqual(default_storage.accessed_time("test.txt"), modified_time)
            self.assertEqual(default_storage.created_time("test.txt"), modified_time)

    def test_get_modified_time(self):
        tzname = "Asia/Shanghai"
        with self.settings(USE_TZ = False, TIME_ZONE = tzname), self.save_file():
            modified_time = default_storage.get_modified_time("test.txt")
            logging.info("modified time: %s", modified_time)
            logging.info("is naive: %s", is_naive(modified_time))
            self.assertTrue(is_naive(modified_time))
            # Check that the timestamps are roughly equals in the correct timezone
            self.assertLess(abs(modified_time - timezone.now()), timedelta(seconds=10))
            self.assertEqual(default_storage.get_accessed_time("test.txt"), modified_time)
            self.assertEqual(default_storage.get_created_time("test.txt"), modified_time)
        with self.settings(USE_TZ = True, TIME_ZONE = tzname), self.save_file():
            modified_time = default_storage.get_modified_time("test.txt")
            logging.info("modified time: %s", modified_time)
            logging.info("is naive: %s", is_naive(modified_time))
            self.assertFalse(is_naive(modified_time))
            # Check that the timestamps are roughly equals in the correct timezone
            self.assertLess(abs(modified_time - timezone.now()), timedelta(seconds=10))
            self.assertEqual(default_storage.get_accessed_time("test.txt"), modified_time)
            self.assertEqual(default_storage.get_created_time("test.txt"), modified_time)
        with self.save_file():
            modified_time = default_storage.get_modified_time("test.txt")
            logging.info("modified time: %s", modified_time)
            logging.info("is naive: %s", is_naive(modified_time))
            self.assertFalse(is_naive(modified_time))
            # Check that the timestamps are roughly equals in the correct timezone
            self.assertLess(abs(modified_time - timezone.now()), timedelta(seconds=10))
            self.assertEqual(default_storage.get_accessed_time("test.txt"), modified_time)
            self.assertEqual(default_storage.get_created_time("test.txt"), modified_time)

    def test_listdir(self):
        self.assertFalse(default_storage.exists("test"))
        with self.save_file(), self.save_file(name = "test/test.txt"):
            self.assertEqual(default_storage.listdir("."), ([u'media/test/'], [u'media/test.txt']))
            self.assertEqual(default_storage.listdir("test"), ([], [u'media/test/test.txt']))
            self.assertEqual(default_storage.listdir("test/"), ([], [u'media/test/test.txt']))
            self.assertEqual(default_storage.listdir("test/test/"), ([], []))

    def test_endpoint_url(self):
        with self.settings(OSS_ENDPOINT = "https://oss-cn-shanghai.aliyuncs.com"), self.save_file() as name:
            self.assertEqual(name, "test.txt")
            self.assertEqual(default_storage.open(name).read(), b"test")

    def test_overwrite(self):
        with self.save_file(content=b'aaaaaa') as name_1:
            self.assertEqual(name_1, "test.txt")
            handle = default_storage.open(name_1)
            self.assertEqual(str(handle.read()), b"aaaaaa")
        with self.save_file(content=b'bbbbbb') as name_2:
            self.assertEqual(name_2, "test.txt")
            handle = default_storage.open(name_2)
            self.assertEqual(str(handle.read()), b"bbbbbb")

    def test_overwrite_cn(self):
        objname = to_unicode("本地文件名.txt")
        logging.info("objname: %s", objname)
        with self.save_file(objname, content=u'我的座右铭') as name_1:
            self.assertEqual(name_1, objname)
            handle = default_storage.open(name_1)
            self.assertEqual(handle.read(), '我的座右铭')
        with self.save_file(objname, content=u'这是一个测试') as name_2:
            self.assertEqual(name_2, objname)
            handle = default_storage.open(name_2)
            self.assertEqual(handle.read(), '这是一个测试')

    def test_static_url(self):
        with self.save_file(storage=staticfiles_storage):
            url = staticfiles_storage.url("test.txt", 60)
            logging.info("url: %s", url)
            response = requests.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"test")
            self.assertEqual(response.headers['Content-Type'], b"text/plain")

    def test_configured_url(self):
        with self.settings(MEDIA_URL= "/media/"), self.save_file():
            url = default_storage.url("test.txt", 60)
            logging.info("url: %s", url)
            response = requests.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"test")
            self.assertEqual(response.headers['Content-Type'], b"text/plain")

    def test_default_logger_basic(self):
        # verify default logger
        self.assertEqual(defaults.logger(), logging.getLogger())

        # verify custom logger
        custom_logger = logging.getLogger('test')
        defaults.log = custom_logger

        self.assertEqual(defaults.logger(), custom_logger)
