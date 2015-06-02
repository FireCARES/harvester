# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collections import OrderedDict
from datetime import datetime
from harvester import __version__
from harvester.util import get_class, pretty_time_delta, update_dict, query_dict
from celery.contrib.methods import task
import logging
import traceback
import requests
import json
import os
import re


class BadWorkFileFormat(Exception):
    pass


class InvalidWorkProvider(Exception):
    pass


class Runner(object):
    @classmethod
    def from_file(cls, filename):
        return cls(json.load(open(filename)))

    def __init__(self, content):
        self._content = {
            "layer": None,
            "provider": None,
            "provider_parameters": {},
            "country": None,
            "state_province": None,
            "city": None,
            "stateco_fips": None,
            "starting_chunk_size": None,
            "id_field": "OBJECTID",
            "srs": None,
            "min_id": None,
            "max_id": None,
            "load_destination": None,
            "load_provider": None,
            "load_provider_parameters": {},
            "extract_only": None,
            "webhook": {
                "done": None,
                "fail": None
            },
            "pruners": [],
            "transformers": []
        }
        self._content.update(content)
        self._provider = None
        self._provider_parameters = None
        self._load_provider = None
        self._load_provider_parameters = None
        self._pruners = []
        self._transformers = []
        self.validate()
        self.count = 0

    def merge(self, settings):
        def munge_from_json_key(s):
            return re.sub('-', '_', s)

        for s in settings:
            qry = munge_from_json_key(s)
            # In that special case that we want to update ALL of the children
            val = query_dict(self._content, qry)
            if type(val) is dict:
                for key in val:
                    update_dict(self._content, settings[s], qry + '.' + key)
                    logging.info('Updated work settings under {0} with {1}'.format(qry, settings[s]))
            else:
                ret = update_dict(self._content, settings[s], qry)
                if ret:
                    logging.info('Updated work setting {0} with {1}'.format(qry, settings[s]))

    def validate(self):
        # required for ALL providers
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
                self._provider = get_class(self._content.get('provider'))(self.layer, **self.provider_parameters)
            except ImportError:
                raise InvalidWorkProvider('Missing work provider "{0}"'.format(self._content.get('provider')))
        return self._provider

    @property
    def provider_parameters(self):
        if not self._provider_parameters:
            self._provider_parameters = dict(self._content.get('provider_parameters'))
        return self._provider_parameters

    @property
    def load_provider(self):
        if not self._load_provider:
            try:
                self._load_provider = get_class(self._content.get('load_provider'))
            except ImportError:
                raise InvalidWorkProvider('Missing data loading provider "{0}"'.format(self._content.get('load_provider')))
        return self._load_provider

    @property
    def load_provider_parameters(self):
        if not self._load_provider_parameters:
            self._load_provider_parameters = dict(self._content.get('load_provider_parameters'))
        return self._load_provider_parameters

    @property
    def country(self):
        return self._content.get('country')

    @property
    def state_province(self):
        return self._content.get('state_province')

    @property
    def srs(self):
        return self._content.get('srs')

    @property
    def id_field(self):
        return self._content.get('id_field')

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
    def done_webhook(self):
        return self._content.get('webhook', {}).get('done')

    @property
    def fail_webhook(self):
        return self._content.get('webhook', {}).get('fail')

    @property
    def generated_at(self):
        return datetime.strptime(self._content.get('generated_at'), '%Y-%m-%d %H:%M:%S')

    @property
    def generated_version(self):
        return self._content.get('generated_version')

    @property
    def stateco_fips(self):
        return self._content.get('stateco_fips')

    def _parse_class(self, s):
            return s.split(':')[0]

    def _parse_args(self, s):
        if len(s.split(':')) > 1:
            return eval("dict({0})".format(s.split(':')[1]))
        else:
            return {}

    @property
    def pruners(self):
        if not self._pruners:
            self._pruners = []
            for p in self._content.get('pruners'):
                self._pruners.append((get_class(self._parse_class(p)), self._parse_args(p)))
        return self._pruners

    @property
    def transformers(self):
        if not self._transformers:
            self._transformers = []
            for t in self._content.get('transformers'):
                self._transformers.append((get_class(self._parse_class(t)), self._parse_args(t)))
        return self._transformers

    @task
    def do(self):
        try:
            self.started_at = datetime.now()
            try:
                self.count = sum(self.do_extraction().apply().get())
            except NotImplementedError:
                pass
            if not self.extract_only:
                self.do_transform()
                self.load_to(self.load_provider)
        except Exception:
            if self.fail_webhook:
                requests.post(self.fail_webhook, json={'text': self.get_fail_webhook_text(traceback.format_exc())})
        else:
            if self.done_webhook:
                requests.post(self.done_webhook, json={'text': self.get_done_webhook_text()})

    def do_extraction(self):
        return self.provider.extract(self)

    def do_transform(self):
        self.provider.transform(self)

    def load_to(self, dest):
        self.provider.load_to(dest, self, **self.load_provider_parameters)

    def get_done_webhook_text(self):
        return ('Finished harvest on {0}, took {1}, collected {2} features'
                .format(self.layer, pretty_time_delta((datetime.now() - self.started_at).seconds), self.count))

    def get_fail_webhook_text(self, trace):
        return ('HARVEST FAILED on {0} after {1}:\n{2}'
                .format(self.layer, pretty_time_delta((datetime.now() - self.started_at).seconds), trace))

    def transform_features(self, features):
        ret = []
        for f in features:
            cur = f
            for t in self.transformers:
                cur = t[0](cur, **t[1])
            ret.append(cur)
        return ret

    def prune_features(self, features):
        ret = []
        for f in features:
            cur = f
            for p in self.pruners:
                if cur:
                    cur = p[0](cur, **p[1])
            if cur:
                ret.append(cur)
        return ret


class Template(object):
    @staticmethod
    def save_to(filename):
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work-template.json')
        res = json.load(open(p), object_pairs_hook=OrderedDict)
        res['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        res['generated_version'] = __version__
        json.dump(res, open(filename, 'w'), indent=4)
