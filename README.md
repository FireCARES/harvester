# FireCARES Harvester [![Build Status](https://travis-ci.org/profile/FireCARES/harvester.svg)](https://travis-ci.org/profile/FireCARES/harvester)

The FireCARES Harvester is a data collection application used to harvest data from the WWW and ingest into a local datastore for further processing before being pushed into a PostGIS database.

## Assumptions

* Python 2.6+
* Document database store => MongoDB

```bash
virtualenv iaff_harvester
cd iaff_harvester
source bin/activate
pip install -r requirements.pip
```

## Running

*All commands assume that you have your local virtualenv for this project activated and are executed from the root of the project.*

```bash
celery worker -l info
python app.py start_esri_harvest [URL TO ENDPOINT]  # starts the harvesting of an ESRI endpoint
```

### Cleaning the feature cache

```bash
find . -iname "[0-9]*.json" -exec rm {} \;
```
