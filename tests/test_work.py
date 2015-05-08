import unittest
from harvester import work
from tests.util import get_mock_path


class TestWork(unittest.TestCase):
    def setUp(self):
        self.good = work.Runner.from_file(get_mock_path('good_work.json'))

    def test_json_load(self):
        with self.assertRaises(work.BadWorkFileFormat) as context:  # noqa
            work.Runner.from_file(get_mock_path('bad_work.json'))

        self.assertIsNotNone(self.good.done_webhook)
        self.assertIsNotNone(self.good.fail_webhook)
        self.assertNotEqual(self.good.done_webhook, self.good.fail_webhook)

        with self.assertRaises(work.BadWorkFileFormat) as context:  # noqa
            work.Runner({})

    def test_settings_update(self):
        newfail = 'http://www.example.com/newfail'
        newdone = 'http://www.example.com/newdone'
        self.good.merge({'webhook.fail': newfail})
        self.assertEquals(self.good.fail_webhook, newfail)
        self.good.merge({'webhook.done': newdone})
        self.assertEquals(self.good.done_webhook, newdone)
