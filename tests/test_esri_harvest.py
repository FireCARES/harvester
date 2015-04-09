import unittest
from harvester.esri import ESRIHarvester
from harvester.util import chunk
from harvester.transform.esri import RESTJSON
from tests import TEST_DIR
from tests.util import load_mock
import requests_mock
import os


@requests_mock.Mocker()
class TestESRIHarvesting(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_chunking(self, m):
        m.register_uri('GET',
                       'http://www.esriserver.com/arcgis/rest/services/namespace/group/MapServer/0/'
                       'query?where=1%3D1&returnGeometry=false&returnIdsOnly=true&f=pjson',
                       text=load_mock('ids.json'))

        harvester = ESRIHarvester('http://www.esriserver.com/arcgis/rest/services/namespace/group/MapServer/0', data_dir=TEST_DIR)
        self.assertEqual(list(chunk([], 1)), [])
        self.assertEqual(list(chunk([1, 2, 3, 4], 2)), [[1, 2], [3, 4]])
        ids = harvester.get_objectids()
        self.assertEqual(len(list(chunk(ids, 500))), 8)
        self.assertEqual(len(list(chunk(ids, 200))), 20)

    def test_transform_to_geojson(self, m):
        RESTJSON.to_geojson('tests/mock/ex_features.json')
        self.assertTrue(os.path.exists('tests/mock/ex_features.geojson'))
        # Can we run again and overwrite the existing file w/o issue?
        RESTJSON.to_geojson('tests/mock/ex_features.json')
        os.remove('tests/mock/ex_features.geojson')
