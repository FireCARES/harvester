# -*- coding: utf-8 -*-
import unittest
import requests_mock
from harvester.esri import VerbatimHarvester, ESRIHarvester
from tests import TEST_DIR
import shutil
import os
import re


def exists(f):
    return os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), f))


@requests_mock.Mocker()
class TestFilebasedCache(unittest.TestCase):
    def setUp(self):
        self.mocks = os.path.join(os.path.dirname(__file__), 'mock')
        if os.path.exists(TEST_DIR):
            shutil.rmtree(TEST_DIR)
        pass

    def tearDown(self):
        pass

    def test_get_google(self, m):
        m.register_uri('GET', re.compile('^http:\/\/www\.google\.com.*'), text='')
        v = VerbatimHarvester(data_dir='cache_test')
        v.get('http://www.google.com')
        self.assertTrue(exists(TEST_DIR))
        self.assertTrue(exists(TEST_DIR + '/http/www.google.com/index'))
        v.get('http://www.google.com/fname')
        self.assertTrue(exists(TEST_DIR + '/http/www.google.com/fname'))
        v.get('http://www.google.com/fname?query=test&second=0')
        self.assertTrue(exists(TEST_DIR + '/http/www.google.com/fnamequery=test&second=0'))

    def test_get_count(self, m):
        m.register_uri('GET', 'http://www.esriserver.com/arcgis/rest/services/namespace/group/MapServer/0/'
                       'query?where=1%3D1&returnCountOnly=true&f=pjson',
                       text=open(os.path.join(self.mocks, 'count.json')).read())
        m.register_uri('GET',
                       'http://www.esriserver.com/arcgis/rest/services/namespace/group/MapServer/0/'
                       'query?where=1%3D1&returnGeometry=false&returnIdsOnly=true&f=pjson',
                       text=open(os.path.join(self.mocks, 'ids.json')).read())
        harvester = ESRIHarvester('http://www.esriserver.com/arcgis/rest/services/namespace/group/MapServer/0', data_dir=TEST_DIR)
        harvester.get_feature_count()
        harvester.get_objectids()
        self.assertTrue(exists(TEST_DIR + '/www_esriserver_com_arcgis_rest_services_namespace_group_MapServer_0_query/count.json'))
        self.assertTrue(exists(TEST_DIR + '/www_esriserver_com_arcgis_rest_services_namespace_group_MapServer_0_query/ids.json'))
