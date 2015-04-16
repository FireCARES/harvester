# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collections import OrderedDict
from datetime import datetime
from harvester import __version__
from harvester.util import get_class
from celery.contrib.methods import task
import json
import os


class BadWorkFileFormat(Exception):
    pass


class InvalidWorkProvider(Exception):
    pass


class Runner(object):
    @classmethod
    def from_file(cls, filename):
        return cls(json.load(open(filename)))

    def __init__(self, content):
        self._content = content
        self._provider = None
        self._load_provider = None
        self.validate()

    def validate(self):
        for p in ['layer', 'provider', 'country', 'state_province', 'city', 'load_provider',
                  'load_destination', 'generated_at', 'generated_version']:
            if not getattr(self, p):
                raise BadWorkFileFormat('Missing field {0} in work'.format(p))

    @property
    def layer(self):
        return self._content.get('layer')

    @property
    def provider(self):
        if not self._provider:
            try:
                self._provider = get_class(self._content.get('provider'))(self.layer)
            except ImportError:
                raise InvalidWorkProvider('Missing work provider "{0}"'.format(self._content.get('provider')))
        return self._provider

    @property
    def load_provider(self):
        if not self._load_provider:
            try:
                self._load_provider = get_class(self._content.get('load_provider'))
            except ImportError:
                raise InvalidWorkProvider('Missing data loading provider "{0}"'.format(self._content.get('load_provider')))
        return self._load_provider

    @property
    def country(self):
        return self._content.get('country')

    @property
    def state_province(self):
        return self._content.get('state_province')

    @property
    def city(self):
        return self._content.get('city')

    @property
    def starting_chunk_size(self):
        return self._content.get('starting_chunk_size', 1000)

    @property
    def min_id(self):
        return self._content.get('min_id', 1)

    @property
    def max_id(self):
        return self._content.get('max_id', 0)

    @property
    def load_destination(self):
        return self._content.get('load_destination')

    @property
    def extract_only(self):
        return self._content.get('extract_only', False)

    @property
    def finished_callback_url(self):
        return self._content.get('finished_callback_url') or None

    @property
    def generated_at(self):
        return datetime.strptime(self._content.get('generated_at'), '%Y-%m-%d %H:%M:%S')

    @property
    def generated_version(self):
        return self._content.get('generated_version')

    @task()
    def do(self):
        self.do_extraction().apply()
        if not self.extract_only:
            self.do_transform()
            self.load_to(self.load_provider)

    def do_extraction(self):
        return self.provider.extract(self)

    def do_transform(self):
        self.provider.transform(self)

    def load_to(self, dest):
        self.provider.load_to(dest, self)


class Template(object):
    @staticmethod
    def save_to(filename):
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work-template.json')
        res = json.load(open(p), object_pairs_hook=OrderedDict)
        res['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        res['generated_version'] = __version__
        json.dump(res, open(filename, 'w'), indent=4)
