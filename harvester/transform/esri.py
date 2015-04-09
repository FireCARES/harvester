import os


class RESTJSON(object):
    @staticmethod
    def to_geojson(filename):
        ofile = os.path.splitext(filename)[0] + '.geojson'
        if os.path.exists(ofile):
            os.remove(ofile)
        # FIXME: i'm a terrible way to transform from ESRI json to geojson
        os.system('ogr2ogr -f "GeoJSON" {0} {1}'.format(ofile, filename))
