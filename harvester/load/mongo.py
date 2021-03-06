from harvester import settings
import pymongo
import json
import re
from datetime import datetime
import logging


class GEOJSONLoader(object):
    @staticmethod
    def load(filename, work, bulk=True, id_field='OBJECTID'):
        if not bulk:
            logging.info("Loading individual features vs bulk loading")

        def _fix_keys(d):
            # http://docs.mongodb.org/manual/reference/limits/#Restrictions%20on%20Field%20Names
            reg = re.compile('\.')
            for k, v in d.items():
                if reg.search(k):
                    d[re.sub('\.', '', k)] = d[k]
                    del d[k]
            return d

        def format_upstream(work, feature):
            return ('{0}/query?objectIds={1}&outFields=*&returnGeometry=true&outSR=4326&f=pjson'
                    .format(work.layer, feature['properties'].get(id_field)))

        with pymongo.MongoClient(settings.MONGO_CONNECTION) as client:
            db = client[settings.MONGO_DATABASE]
            features = json.load(open(filename))['features']
            dest = db[work.load_destination]

            if bulk:
                bulk = dest.initialize_unordered_bulk_op()
            for f in work.transform_features(work.prune_features(features)):
                ins = {'meta':
                       {'layer': work.layer,
                        'country': work.country,
                        'state_province': work.state_province,
                        'city': work.city,
                        'stateco_fips': work.stateco_fips,
                        'provider': work._content.get('provider'),
                        'upstream': format_upstream(work, f),
                        'loaded': datetime.now()
                        },
                       'feature': f}
                _fix_keys(f['properties'])

                if bulk:
                    bulk.find({'feature.properties.OBJECTID': f['properties'][id_field], 'meta.layer': work.layer}) \
                        .upsert().replace_one(ins)
                else:
                    dest.replace_one({'feature.properties.OBJECTID': f['properties'][id_field], 'meta.layer': work.layer},
                                     ins, upsert=True)

            if bulk:
                bulk.execute()
            dest.create_index([('feature.geometry', pymongo.GEOSPHERE)], bits=32)
            dest.create_index([('meta.country', pymongo.ASCENDING),
                               ('meta.state_province', pymongo.ASCENDING),
                               ('meta.city', pymongo.ASCENDING)])
            dest.create_index([('feature.properties.OBJECTID', pymongo.ASCENDING),
                               ('meta.layer', pymongo.ASCENDING)])
