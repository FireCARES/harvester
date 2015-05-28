import unittest
from harvester.providers.readin import ReadInSource, ImproperlyConfigured
from tests import TEST_DIR
import os


class TestReadInSourceHarvesting(unittest.TestCase):

    def test_curl_zip(self):
        harvester = ReadInSource('http://svn.osgeo.org/gdal/trunk/autotest/ogr/data/poly.zip', data_dir=TEST_DIR)

        self.assertTrue(harvester.remote_file)
        self.assertTrue('/vsizip/vsicurl/' in harvester.vsi_string())
        harvester.transform(work=None)
        self.assertTrue(os.path.exists(os.path.join(TEST_DIR, 'poly.geojson')))
        self.assertEqual(harvester.local_file, os.path.join(TEST_DIR, 'poly.geojson'))

    def test_local_zip(self):
        harvester = ReadInSource('poly.zip', data_dir=TEST_DIR)
        self.assertFalse(harvester.remote_file)
        self.assertFalse('/vsicurl/' in harvester.vsi_string())

    def test_compression_type(self):
        harvester = ReadInSource('poly.zip', data_dir=TEST_DIR)
        self.assertTrue(harvester.guess_compression(), 'zip')
        self.assertTrue('/vsizip/' in harvester.vsi_string())

        harvester = ReadInSource('poly.tar', data_dir=TEST_DIR)
        self.assertTrue(harvester.guess_compression(), 'tar')
        self.assertTrue('/vsitar/' in harvester.vsi_string())

        harvester = ReadInSource('poly.tar.gz', data_dir=TEST_DIR)
        self.assertTrue(harvester.guess_compression(), 'gzip')
        self.assertTrue('/vsigzip/' in harvester.vsi_string())

        harvester = ReadInSource('poly.shp', data_dir=TEST_DIR)
        self.assertIsNone(harvester.guess_compression())
        self.assertEqual(harvester.vsi_string(), '')

        with self.assertRaises(ImproperlyConfigured):
            ReadInSource('poly.tar', data_dir=TEST_DIR, compression_type='wtf')
