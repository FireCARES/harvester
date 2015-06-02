# FireCARES Harvester [![Build Status](https://api.travis-ci.org/FireCARES/harvester.svg)](https://travis-ci.org/FireCARES/harvester)

The FireCARES Harvester is a data collection application used to harvest data from the datasources over HTTP
and ingested with simple transformations into a local document store.

## Assumptions

* Python 2.7/3.4
* MongoDB

```bash
virtualenv iaff_harvester
cd iaff_harvester
source bin/activate
pip install .
```

## Running

*All commands assume that you have your local virtualenv for this project activated and are executed from the root of the project.*

```bash
celery worker -l info
harvester generate-work-template [FILENAME]  # create a work definition from the default template
harvester harvester [WORK DEFINITION]  # acts on work defined in the work definition
```

### Work template

```python
{
    "layer": "",  # reference to the layer to harvest (URL/filename/etc)
    "provider": "harvester.providers.esri.RESTHarvester",  # class reference to the provider to use in harvesting/extraction
    "provider_parameters": { },  # kwargs to carry along for provider usage
    "country": "US",
    "state_province": "",
    "city": "",
    "stateco_fips": "00000",
    "starting_chunk_size": 1000,
    "id_field": "OBJECTID",
    "srs": 4326,
    "min_id": null,
    "max_id": null,
    "load_destination": "parcels",  # destination collection/table/file
    "load_provider": "harvester.load.mongo.GEOJSONLoader",  # class reference
    "load_provider_parameters": {},  # kwargs to carry along for the load provider
    "extract_only": false,
    "webhook": {
        "done": null,
        "fail": null
    },
    "pruners": [  # pruners remove entire features, can be passed kwargs via CLASS_REFERENCE:key=value,key2=value2
        "harvester.transform.prune.null_geometry"
    ],
    "transformers": [  # transformers modify a feature before insertion, can be passed kwargs via CLASS_REFERENCE:key=value,key2=value2
        "harvester.transform.alter.fix_duplicate_points"
    ]
}
```


### Cleaning the feature cache

```bash
find . -iname "[0-9]*.json" -exec rm {} \;
```
