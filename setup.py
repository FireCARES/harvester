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
    package_data=get_package_data('.'),
    include_package_data=True,
    install_requires=[
        'Paver==1.2.4',
        'amqp==1.4.6',
        'anyjson==0.3.3',
        'argparse==1.2.1',
        'billiard==3.3.0.19',
        'celery==3.1.17',
        'click==3.3',
        'flake8==2.4.0',
        'gnureadline==6.3.3',
        'kombu==3.0.24',
        'mccabe==0.3',
        'nose==1.3.4',
        'pep8==1.5.7',
        'pyflakes==0.8.1',
        'pymongo==3.0',
        'pytz==2014.10',
        'requests==2.6.0',
        'requests-mock==0.6.0',
        'six==1.9.0',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'harvester = harvester.cli:harvest',
        ],
    },
)
