# -*- coding: utf-8 -*-


def chunk(lst, num):
    """Split list into groups given `num` size."""
    for i in xrange(0, len(lst), num):
        cur = lst[i:i + num]
        yield (min(cur), max(cur))
