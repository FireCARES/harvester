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

### Cleaning the feature cache

```bash
find . -iname "[0-9]*.json" -exec rm {} \;
```
