import unittest
from harvester import work
from tests.util import get_mock_path


class TestWork(unittest.TestCase):
    def setUp(self):
        self.good = work.Runner.from_file(get_mock_path('good_work.json'))
        self.good2 = work.Runner.from_file(get_mock_path('good_work2.json'))
        self.good3 = work.Runner.from_file(get_mock_path('good_work3.json'))

    def test_json_load(self):
        with self.assertRaises(work.BadWorkFileFormat) as context:  # noqa
            work.Runner.from_file(get_mock_path('bad_work.json'))

        self.assertIsNotNone(self.good.done_webhook)
        self.assertIsNotNone(self.good.fail_webhook)
        self.assertNotEqual(self.good.done_webhook, self.good.fail_webhook)

        with self.assertRaises(work.BadWorkFileFormat) as context:  # noqa
            work.Runner({})

        self.assertEqual(self.good.transformers, [])
        self.assertEqual(self.good.pruners, [])

        self.assertGreater(len(self.good3.transformers), 0)
        self.assertGreater(len(self.good3.pruners), 0)

    def test_settings_update(self):
        newfail = 'http://www.example.com/newfail'
        newdone = 'http://www.example.com/newdone'
        self.good.merge({'webhook.fail': newfail})
        self.assertEquals(self.good.fail_webhook, newfail)
        self.good.merge({'webhook.done': newdone})
        self.assertEquals(self.good.done_webhook, newdone)

    def test_backwards_compatability(self):
        newdone = 'http://www.example.com/newdone'
        self.good2.merge({'webhook': newdone})
        self.assertEquals(self.good2.done_webhook, newdone)

    def test_provider_parameters(self):
        self.assertEqual(self.good3.provider_parameters.get('srs'), 4326)
        self.assertEqual(self.good3.load_provider_parameters.get('id_field'), 'OBJECTID')
