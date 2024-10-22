#!/usr/bin/env python

import re


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


version = ''
with open('django_oss_storage/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')


with open('README.md', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(
    name='django-oss-storage-v2',
    version=version,
    description='Django Aliyun OSS (Object Storage Service) storage v2, compatible with Django 5.1+',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=['django_oss_storage'],
    install_requires=['django>=1.10',
                      'oss2>=2.3.3'],
    include_package_data=True,
    url='https://github.com/twisker/django-oss-storage',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Framework :: Django',
    ],
)
