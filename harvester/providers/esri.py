"""ESRI REST-based harvesting utility functions

Note: ALL functions expect a URL to the map layer endpoint (eg. endswith
something similar to "/MapServer/0")
"""

from __future__ import absolute_import
import glob
import json
import os
import re
import sys
import urlparse
from harvester.http import CachableHTTPHarvester
from harvester.transform.esri import ESRIJSON
from harvester.util import chunk
from harvester.validators import ESRIREST
from celery import group
from celery.contrib.methods import task
from celery.utils.log import get_task_logger
import logging

log = get_task_logger(__name__)


class RESTHarvester(CachableHTTPHarvester):
    QUERY_COUNT = 'query?where=1%3D1&returnCountOnly=true&f=pjson'
    QUERY_OBJECTIDS = 'query?where=1%3D1&returnGeometry=false&returnIdsOnly=true&f=pjson'
    QUERY_FEATURES = 'query?where=objectid>={0}+AND+objectid<={1}&outSR={2}&outFields=*&returnGeometry=true&f=pjson'

    def __init__(self, url, sr=4326, *args, **kwargs):
        super(RESTHarvester, self).__init__(*args, **kwargs)
        self.url = self.__reformat_url(url)
        self.sr = sr

    def __reformat_url(self, url):
        if not url.endswith('/'):
            return url + '/'
        else:
            return url

    def get_cache_dir(self):
        return os.path.dirname(self.url_to_file(self.url + self.QUERY_FEATURES.format(0, 0, 0)))

    def url_to_file(self, url):
        res = urlparse.urlparse(url)
        qs = urlparse.parse_qs(res.query)
        path, filename = None, None
        # FIXME from being so bad
        if 'where' in qs and 'outFields' in qs:
            filename = '_'.join(re.findall('(\d+)', qs['where'][0])) + '.json'
        elif 'returnCountOnly' in qs:
            filename = 'count.json'
        elif 'returnIdsOnly' in qs:
            filename = 'ids.json'
        path = res.netloc.replace('.', '_') + res.path.replace('/', '_')
        return os.path.join(self.data_dir, path, filename or '')

    def get_feature_count(self):
        resp = self.get(self.url + self.QUERY_COUNT)
        return json.loads(resp)['count']

    def get_objectids(self):
        resp = self.get(self.url + self.QUERY_OBJECTIDS)
        return json.loads(resp)['objectIds']

    def get_features(self, start, end):
        dest = self.url + self.QUERY_FEATURES.format(start, end, self.sr)
        resp = self.get(dest)
        return json.loads(resp)

    def get_cached_feature_files(self):
        return glob.glob(self.get_cache_dir() + '/[0-9]*.json')

    def get_cached_files(self):
        return glob.glob(self.get_cache_dir() + '/*.json')

    def get_cached_geojson_files(self):
        return glob.glob(self.get_cache_dir() + '/*.geojson')

    def clear_cache(self, everything=False):
        files = []
        if everything:
            files = self.get_cached_files()
        else:
            files = self.get_cached_feature_files()
        for f in files:
            logging.info('Removing {0} from cache'.format(f))
            os.unlink(f)

    @task(rate_limit="30/m", num_retries=3)
    def harvest_range(self, c):
        """Pull range of features with automatic from start/end objectIds."""

        start, end = min(c), max(c)
        log.info('Harvesting object ids between {0} and {1}'.format(start, end))

        try:
            # Split chunk up if "exceeded transfer limit" or if the set of objectIds != what was expected
            features = self.get_features(start, end)

            if not ESRIREST.is_retrieval_limit_exceeded(features) and ESRIREST.validate_objectids_exist(features, c):
                return features
            else:
                self.clear_feature_cache(start, end)
                c1 = c[:len(c) / 2]
                c2 = c[len(c) / 2:]
                log.info('Splitting feature chunk in half, feature retrieval limit exceeded/OBJECTIDs missing, new chunks {0} and {1}'
                         .format((min(c1), max(c1)), (min(c2), max(c2))))

                return group(self.harvest_range.s(c1).set(countdown=10), self.harvest_range.s(c2).set(countdown=10))()
        except Exception as exc:
            self.harvest_range.retry(exc=exc, countdown=15, max_retries=3)

    def split_job(self, start=1, end=0, job_size=1000):
        """Split job into chunks and returns set of tasks given start/end objectIds."""

        log.info('Started pull for {0} in chunks of {1} features (objectIds {2} - {3})'
                 .format(self.url, job_size, start, end))
        ids = self.get_objectids()
        ids.sort()
        chunks = list(chunk([i for i in ids if i >= start and i <= (end or sys.maxint)], job_size))
        log.debug('Chunks: {0}'.format([(min(c), max(c)) for c in chunks]))
        return group(self.harvest_range.s(c) for c in chunks)

    def extract(self, work):
        logging.info('Starting extraction against {0}'.format(work.layer))
        return self.split_job(work.min_id, work.max_id, work.starting_chunk_size)

    def transform(self, work):
        files = self.get_cached_feature_files()
        for f in files:
            logging.info('Transforming {0} to geojson'.format(f))
            ESRIJSON.to_geojson(f)

    def load_to(self, cls, work):
        for f in self.get_cached_geojson_files():
            logging.info('Loading features from {0}'.format(f))
            cls.load(f, work)
