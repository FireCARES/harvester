#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re
import os
from setuptools import find_packages

name = 'firecares-harvester'
package = 'harvester'
description = 'FireCARES Harvester'
url = 'https://github.com/FireCARES/harvester'
author = 'Prominent Edge'
author_email = 'contact@prominentedge.com'
license = 'MIT'


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


setup(
    name=name,
    version=get_version(package),
    url=url,
    license=license,
    description=description,
    author=author,
    author_email=author_email,
    packages=find_packages(exclude=["tests.*", "tests"]),
    package_data=get_package_data(package),
    install_requires=[
        'Jinja2==2.7.3',
        'MarkupSafe==0.23',
        'Paver==1.2.4',
        'Pygments==2.0.2',
        'amqp==1.4.6',
        'anyjson==0.3.3',
        'argparse==1.2.1',
        'backports.ssl-match-hostname==3.4.0.2',
        'billiard==3.3.0.19',
        'celery==3.1.17',
        'certifi==14.05.14',
        'click==3.3',
        'colorama==0.3.3',
        'flake8==2.4.0',
        'gnureadline==6.3.3',
        'httplib2==0.9',
        'ipdb==0.8',
        'ipython==3.0.0',
        'jsonschema==2.4.0',
        'kombu==3.0.24',
        'logutils==0.3.3',
        'mccabe==0.3',
        'mistune==0.5',
        'nose==1.3.4',
        'nose-timer==0.4.3',
        'pep8==1.5.7',
        'ptyprocess==0.4',
        'pyflakes==0.8.1',
        'pyrabbit==1.1.0',
        'pytz==2014.10',
        'pyzmq==14.5.0',
        'rainbow-logging-handler==2.2.2',
        'requests==2.6.0',
        'requests-mock==0.6.0',
        'six==1.9.0',
        'termcolor==1.1.0',
        'terminado==0.5',
        'tornado==4.1',
        'wsgiref==0.1.2',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'harvester = harvester.app:harvest',
        ],
    },
)
