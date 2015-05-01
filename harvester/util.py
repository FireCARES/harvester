# -*- coding: utf-8 -*-


def chunk(lst, num):
    """Split list into groups given `num` size."""
    for i in xrange(0, len(lst), num):
        cur = lst[i:i + num]
        yield cur


def flatten(l):
    """[[1,2],[3,4],[1,2,3]] ==> [1,2,3,4,1,2,3]"""
    return [i for sl in l for i in sl]


def inverse_chunks(l):
    """Expects 2d list of lists (bivalue int)

    ex. [[1,4],[9,12],[15, 24]] ==> [[5,8],[13,14]]
    """
    if len(l) < 2:
        return None
    return [[v[0] + 1, v[1] - 1] for v in list(chunk(flatten(l)[1:-1], 2))]


def collapse(l):
    """Collapses continguous separate pseudo-ranges (represented as bivalue list)
    into inclusive distinct pseudo-ranges.

    Expects 2d list of lists (bivalue int)

    ex. [[1,4],[5,10],[15,25]] ==> [[1,10],[15,25]]
    """
    ret = []
    l.sort(key=lambda x: x[0])
    ret.append(l[0][0])
    ret.append(max(l, key=lambda x: x[1])[1])
    for idx, i in enumerate(l):
        if idx < len(l) - 1 and i[1] + 1 >= l[idx+1][0]:
            continue
        else:
            if idx < len(l) - 1:
                ins = len(ret) - 1
                ret.insert(ins, l[idx+1][0])
                ret.insert(ins, i[1])
    return list(chunk(ret, 2))


# Snagged from http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
def get_class(cls):
    parts = cls.split('.')
    module = '.'.join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


# Snagged from https://gist.github.com/thatalextaylor/7408395
def pretty_time_delta(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%dd%dh%dm%ds' % (days, hours, minutes, seconds)
    elif hours > 0:
        return '%dh%dm%ds' % (hours, minutes, seconds)
    elif minutes > 0:
        return '%dm%ds' % (minutes, seconds)
    else:
        return '%ds' % (seconds,)
