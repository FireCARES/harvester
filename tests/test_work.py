import unittest
from harvester import work
from tests.util import get_mock_path


class TestWork(unittest.TestCase):
    def test_json_load(self):
        with self.assertRaises(work.BadWorkFileFormat) as context:  # noqa
            work.Runner.from_file(get_mock_path('bad_work.json'))

        work.Runner.from_file(get_mock_path('good_work.json'))

        with self.assertRaises(work.BadWorkFileFormat) as context:  # noqa
            work.Runner({})
