import os


def load_mock(fname):
    return open(get_mock_path(fname)).read()


def get_mock_path(fname):
    return os.path.join(os.path.dirname(__file__), 'mock', fname)
