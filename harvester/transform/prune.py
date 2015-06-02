# -*- coding: utf-8 -*-
import logging


def null_geometry(feature):
    if feature.get('geometry') is None:
        logging.info('Found null geometry for {0}, pruning'.format(feature.get('properties').get('OBJECTID')))
        return None
    else:
        return feature


# See http://docs.python-guide.org/en/latest/writing/gotchas/#mutable-default-arguments
def prune_by_ids(feature, ids=None):
    if ids is None:
        ids = []
    if feature.get('properties').get('OBJECTID') in ids:
        logging.info('Pruned out feature {0}'.format(feature.get('properties').get('OBJECTID')))
        return None
    else:
        return feature
