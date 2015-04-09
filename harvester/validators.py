# -*- coding: utf-8 -*-


class ESRIREST(object):
    @staticmethod
    def is_retrieval_limit_exceeded(features):
        return features.get('exceededTransferLimit', False)

    @staticmethod
    def validate_objectids_exist(features, chunk):
        return (set(map(lambda x: x.get('attributes').get('OBJECTID'), features.get('features')))
                - set(chunk) == set())
