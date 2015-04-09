# -*- coding: utf-8 -*-
from __future__ import absolute_import

from harvester.util import chunk
from harvester.validators import ESRIREST
from celery import group, Celery
from celery.utils.log import get_task_logger
import sys

app = Celery('harvester.workers')
log = get_task_logger(__name__)


@app.task(rate_limit="30/m", num_retries=3)
def harvest_range(harvester, c):
    """Pull range of features with automatic from start/end objectIds."""

    start, end = min(c), max(c)
    log.info('Harvesting object ids between {0} and {1}'.format(start, end))

    try:
        # Split chunk up if "exceeded transfer limit" or if the set of objectIds != what was expected
        features = harvester.get_features(start, end)

        if not ESRIREST.is_retrieval_limit_exceeded(features) and ESRIREST.validate_objectids_exist(features, c):
            return features
        else:
            harvester.clear_feature_cache(start, end)
            c1 = c[:len(c) / 2]
            c2 = c[len(c) / 2:]
            log.info('Splitting feature chunk in half, feature retrieval limit exceeded/OBJECTIDs missing, new chunks {0} and {1}'
                     .format((min(c1), max(c1)), (min(c2), max(c2))))

            return group(harvest_range.s(harvester, c1).set(countdown=10), harvest_range.s(harvester, c2).set(countdown=10))()
    except Exception as exc:
        harvest_range.retry(exc=exc, countdown=15, max_retries=3)


def split_job(harvester, start=1, end=0, job_size=1000):
    """Split job into chunks and returns set of tasks given start/end objectIds."""

    log.info('Started pull for {0} in chunks of {1} features (objectIds {2} - {3})'
             .format(harvester.url, job_size, start, end))
    ids = harvester.get_objectids()
    ids.sort()
    chunks = list(chunk([i for i in ids if i >= start and i <= (end or sys.maxint)], job_size))
    log.debug('Chunks: {0}'.format([(min(c), max(c)) for c in chunks]))
    return group(harvest_range.s(harvester, c) for c in chunks)
