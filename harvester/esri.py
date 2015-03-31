"""ESRI REST-based harvesting utility functions

Note: ALL functions expect a URL to the map layer endpoint (eg. endswith
something similar to "/MapServer/0")
"""

import urlparse
import re
import json
import os
from harvester.http import CachableHTTPHarvester


class ESRIHarvester(CachableHTTPHarvester):
    QUERY_COUNT = 'query?where=1%3D1&returnCountOnly=true&f=pjson'
    QUERY_OBJECTIDS = 'query?where=1%3D1&returnGeometry=false&returnIdsOnly=true&f=pjson'
    QUERY_FEATURES = 'query?where=objectid>={0}+AND+objectid<={1}&outFields=*&returnGeometry=true&f=pjson'

    def __init__(self, url, *args, **kwargs):
        super(ESRIHarvester, self).__init__(*args, **kwargs)
        self.url = self.__reformat_url(url)

    def __reformat_url(self, url):
        if not url.endswith('/'):
            return url + '/'
        else:
            return url

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
        dest = self.url + self.QUERY_FEATURES.format(start, end)
        resp = self.get(dest)
        return json.loads(resp)
