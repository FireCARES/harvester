# -*- coding: utf-8 -*-
MONGO_CONNECTION = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'harvester'
DATA_DIR = 'data'

try:
    from harvester.local_settings import *  # noqa
except Exception:
    pass
