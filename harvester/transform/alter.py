# -*- coding: utf-8 -*-

import logging
import random


def fix_duplicate_points(feature):
    """
    Cleans up the duplicated points in POLYGON geometries by removal
    """
    def perturbate_point(pt, coords):
        return [pt[0] - random.random() / 1000000, pt[1] - random.random() / 1000000]

    def histogram(coords):
        hist = {}
        for c in coords:
            hist[c] = hist.get(c, 0) + 1
        return hist

    def rotate(d):
        """
        Takes a dictionary w/ potentially-duplicated values and rotates the values to
        become the keys and the keys as values in a list
        """
        ret = {}
        for x in d:
            if d[x] not in ret:
                ret[d[x]] = [x]
            else:
                ret[d[x]].append(x)
        return ret

    if feature['geometry'] and feature['geometry']['type'] in ['Polygon']:
        for ringidx, coords in enumerate(feature['geometry']['coordinates']):
            items = [tuple(c) for c in coords]
            # Chop off the final point as they will always be the same as the first
            diff = len(items[:-1]) - len(set(items[:-1]))
            if diff:
                # Do a pseudo histogram
                hist = histogram(items[:-1])
                trimmed_hist = filter(lambda a: hist[a] > 1, hist)
                logging.info("# of unique duplicates {0}".format(len(trimmed_hist)))
                indexes = {i: x for i, x in enumerate(items[:-1]) for y in trimmed_hist if y == x}
                to_remove = [i for s in [sorted(x[1])[1:] for x in rotate(indexes).items()] for i in s]
                logging.info("DUPS FOR {0} => {1}".format(feature['properties']['OBJECTID'], str(to_remove)))
                # Remove the dups
                for del_idx in reversed(sorted(to_remove)):
                    del feature['geometry']['coordinates'][ringidx][del_idx]
                logging.info("New geometry length {0}, old {1}".format(len(feature['geometry']['coordinates'][ringidx]), len(items)))

    return feature
