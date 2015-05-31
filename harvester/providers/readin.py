from __future__ import absolute_import

import logging
import mimetypes
import os

from harvester.http import CachableHTTPHarvester
from celery.utils.log import get_task_logger

log = get_task_logger(__name__)


class ImproperlyConfigured(Exception):
    pass


class ReadInSource(CachableHTTPHarvester):
    """
    Implements https://trac.osgeo.org/gdal/wiki/UserDocs/ReadInZip.
    """
    SUPPORTED_COMPRESSION_TYPES = 'gzip zip tar'.split()

    def __init__(self, url, sr=4246, compression_type=None, *args, **kwargs):
        super(ReadInSource, self).__init__(*args, **kwargs)
        self.url = url
        self.sr = sr
        self.compression_type = compression_type or self.guess_compression()

        if self.compression_type and self.compression_type not in self.SUPPORTED_COMPRESSION_TYPES:
            raise ImproperlyConfigured('Compression type {0} is not supported.'.format(self.compression_type))

    def extract(self, work):
        """
        Extraction is handled in the transform step.
        """
        raise NotImplementedError

    def guess_compression(self):
        """
        Uses the mimetype builtin to guess the compression.
        """
        mime_type, subtype = mimetypes.guess_type(self.url)

        if mime_type == 'application/zip':
            return 'zip'

        if mime_type == 'application/x-tar':
            if subtype == 'gzip':
                return 'gzip'

            if subtype is None:
                return 'tar'

    @property
    def remote_file(self):
        """
        Returns True if the file is a remote file, false if its local.
        """
        return self.url.startswith('http') or self.url.startswith('ftp')

    def vsi_string(self):
        """
        Returns the correct VSI string (https://trac.osgeo.org/gdal/wiki/UserDocs/ReadInZip) based on certain
        conditions.
        """
        vsi_string = ''

        if self.compression_type:
            vsi_string = '/vsi{0}/'.format(self.compression_type)

        if self.remote_file:
            vsi_string += '/vsicurl/'

        return vsi_string.replace('//', '/')

    def load_to(self, cls, work):
        return cls.load(self.local_file, work)

    def in_srs_string(self):
        if self.sr:
            return '-s_srs {0}'.format(self.sr)
        return ''

    def transform(self, work):
        logging.info('Transforming {0} to geojson'.format(self.url))

        self.sr = getattr(work, 'srs', None)
        self.local_file = os.path.join(self.data_dir, os.path.splitext(os.path.split(self.url)[1])[0] + '.geojson')

        command = 'ogr2ogr -t_srs EPSG:4326 {3} -f "GeoJSON" {0} {1}{2}'.format(self.local_file, self.vsi_string(),
                                                                                self.url, self.in_srs_string())
        logging.debug('ReadIn provider gdal command: {0}'.format(command))
        os.system(command)
