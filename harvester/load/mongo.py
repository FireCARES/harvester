from harvester import settings
import pymongo
import json
import re
from datetime import datetime


class GEOJSONLoader(object):
    @staticmethod
    def load(filename, work):
        def _fix_keys(d):
            # http://docs.mongodb.org/manual/reference/limits/#Restrictions%20on%20Field%20Names
            reg = re.compile('\.')
            for k, v in d.items():
                if reg.search(k):
                    d[re.sub('\.', '', k)] = d[k]
                    del d[k]
            return d

        with pymongo.MongoClient(settings.MONGO_CONNECTION) as client:
            db = client[settings.MONGO_DATABASE]
            features = json.load(open(filename))['features']

            for f in features:
                ins = {'meta':
                       {'layer': work.layer,
                        'country': work.country,
                        'state_province': work.state_province,
                        'city': work.city,
                        'provider': work._content.get('provider'),
                        'loaded': datetime.now()
                        },
                       'feature': f}
                _fix_keys(f['properties'])
                # TODO: Make this query unique across BOTH OBJECTID AND meta.layer!
                db[work.load_destination].replace_one({'feature.properties.OBJECTID': f['properties']['OBJECTID']},
                                    ins, upsert=True)
            db.test.create_index([('feature.geometry', pymongo.GEOSPHERE)])