# -*- coding: utf-8 -*-
import requests
import six.moves.urllib.parse as urlparse
import os
import click
from six import StringIO
import logging

log = logging.getLogger(__name__)


class CachableHTTPHarvester(object):
    """Faux abstract class, this class doesn't have the complete wiring necessary, must implement `url_to_file`"""
    def __init__(self, cache_enabled=True, data_dir='data'):
        self.cache_enabled = cache_enabled
        self.interactive = True
        self.data_dir = data_dir

    def get_cached_response(self, url):
        src = self.url_to_file(url)
        if os.path.exists(src):
            with open(src) as f:
                return f.read()
        else:
            return None

    def has_cached_response(self, url):
        f = self.url_to_file(url)
        return os.path.exists(f) and os.path.getsize(f)

    def get(self, url, transform_on_save=lambda x: x.getvalue()):
        if self.cache_enabled and self.has_cached_response(url):
            log.debug('Pulling from cache for %s' % (url,))
            return self.get_cached_response(url)
        else:
            log.debug('No cache, pulling for %s' % (url,))
            resp = requests.get(url, stream=True)
            return self.write_raw_response(resp, transform=transform_on_save)

    def write_raw_response(self, resp, transform=lambda x: x.getvalue()):
        path = self.url_to_file(resp.url)

        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        buf = StringIO()
        total_length = int(resp.headers.get('content-length', 0))

        if total_length:
            if self.interactive:
                with click.progressbar(resp.iter_content(chunk_size=1024), length=(total_length / 1024) + 1) as chunk:
                    for c in chunk:
                        if chunk:
                            buf.write(c)
            else:
                for chunk in resp.iter_content(chunk_size=1024):
                    buf.write(chunk)
        else:
            buf.write(resp.text)

        with open(path, 'w') as f:
            f.write(transform(buf))

        log.info('Wrote results to %s' % (path, ))
        return buf.getvalue()


class VerbatimHarvester(CachableHTTPHarvester):
    def __init__(self, *args, **kwargs):
        super(VerbatimHarvester, self).__init__(*args, **kwargs)

    def url_to_file(self, url):
        parsed = urlparse.urlparse(url)
        path = '/'.join([parsed.scheme, parsed.netloc, os.path.split(parsed.path)[0]])
        filename = os.path.split(parsed.path)[1] + parsed.query or 'index' + parsed.query
        return os.path.join(self.data_dir, path, filename)
