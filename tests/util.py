import os


def load_mock(fname):
    return open(os.path.join(os.path.dirname(__file__), 'mock', fname)).read()
