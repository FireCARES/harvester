# -*- coding: utf-8 -*-
from __future__ import absolute_import

from harvester.util import chunk
from celery import group, Celery
from celery.utils.log import get_task_logger

app = Celery('harvester.workers')
log = get_task_logger(__name__)


@app.task(retries=3)
def harvest_range(harvester, start, end):
    """Pull range of features with automatic from start/end objectIds."""
    log.info('Harvesting object ids between {0} and {1}'.format(start, end))
    try:
        #TODO: Add in sliding chunk size window when the results comes back w/
        # "exceeded transfer limit" or if the set of objectIds != what was expected
        return harvester.get_features(start, end)
    except Exception as exc:
        harvest_range.retry(exc=exc, countdown=15, max_retries=3)


def split_job(harvester, start=0, end=1000, job_size=100):
    """Split job into chunks and returns set of tasks given start/end objectIds."""
    log.info('Started pull for {0} in chunks of {1} features (objectIds {2} - {3})'.format(harvester.url, job_size, start, end))
    ids = harvester.get_objectids()
    ids.sort()
    chunks = list(chunk([i for i in ids if i >= start and i <= end], job_size))
    log.debug("Chunks: {0}".format(chunks))
    return group(harvest_range.s(harvester, *c) for c in chunks)
