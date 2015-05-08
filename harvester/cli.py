# -*- coding: utf-8 -*-
import click
import logging
import logging.config
import re
from harvester import work
from harvester.providers.esri import RESTHarvester
from harvester.load.mongo import GEOJSONLoader


LOG_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': 'out.log',
            'mode': 'a',
        },
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s(%(lineno)s): %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s %(module)-17s line:%(lineno)-4d '
            '%(levelname)-8s %(message)s',
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },
    }
}

logging.config.dictConfig(LOG_SETTINGS)
log = logging.getLogger(__name__)


@click.group()
@click.pass_context
@click.version_option()
def cli(ctx):
    """Harvester CLI."""
    pass


@cli.command('generate-work-template')
@click.argument('filename', type=click.Path())
@click.pass_context
def generate_work_template(ctx, filename):
    """Generates an empty work template using the given filename"""
    work.Template.save_to(filename)
    log.info('Generated work template at {0}'.format(filename))


@cli.command('harvest')
@click.argument('template', type=click.Path(exists=True))
@click.option('--opt', '-o', multiple=True)
@click.pass_context
def harvest(ctx, template, opt):
    """Performs the work described in the provided template

    Options passed via --opt will override values in the template and should be
    passed using `--opt key=value` format

    Dictionary items with multiple descendents will ALL be updated to the value
    (eg. `-o webhook=http://www.example.com` will update both webhook.fail/webhook.done)
    """
    worker = work.Runner.from_file(template)
    if opt:
        for o in opt:
            # Pull out quoted/unquoted values from `opt` options
            worker.merge({k: v.strip('"') for k, v in re.findall(r'(\S+)=(".*?"|\S+)', o)})
    jobid = worker.do.delay()
    log.info('Enqueued work job {0}'.format(jobid))


@cli.command('esri-pull-feature-count', short_help='Gets the count of features for the given ESRI REST endpoint')
@click.argument('filename', type=click.Path(exists=True))
@click.pass_context
def esri_pull_feature_count(ctx, filename):
    worker = work.Runner.from_file(filename)
    log.info('Total features: {0}'.format(RESTHarvester(worker.layer).get_feature_count()))


@cli.command('esri-pull-ids', short_help='Pull the list of OBJECTIDs from the ESRI REST endpoint')
@click.argument('filename', type=click.Path(exists=True))
@click.pass_context
def esri_pull_ids(ctx, filename):
    worker = work.Runner.from_file(filename)
    ids = RESTHarvester(worker.layer).get_objectids()
    log.info('{0} IDs'.format(len(ids)))


@cli.command('esri-pull-features', short_help='Pull features from an ESRI endpoint, stored in ESRI JSON format')
@click.argument('filename', type=click.Path(exists=True))
@click.pass_context
def esri_pull_features(ctx, filename):
    """Enques feature harvesting jobs for a the given ESRI REST endpoint,
    stores features in ESRI JSON format, pulling using EPSG:4326 srs, starting
    with OBJECTID `start` and ending at OBJECTID `end` or pulling ALL of the features
    when end is "0" [DEFAULT]
    """
    worker = work.Runner.from_file(filename)
    harvester = RESTHarvester(worker.layer)
    result = harvester.split_job(worker.min_id, worker.max_id, worker.starting_chunk_size).delay()
    log.info('Starting harvest of {0} objectids [{1} - {2}] JOB => {3}'.format(worker.layer, worker.min_id, worker.max_id, result))


@cli.command('esri-transform-esri-json', short_help='Manually-transform the ESRI JSON features into traditional geojson')
@click.argument('filename', type=click.Path(exists=True))
@click.pass_context
def esri_transform_esri_json(ctx, filename):
    """Transforms existing ESRI JSON feature lists into geojson equivalents"""
    worker = work.Runner.from_file(filename)
    harvester = RESTHarvester(worker.layer)
    harvester.transform(worker)


@cli.command('esri-load-geojson', short_help='Loads the existing geojson for this endpoint')
@click.argument('filename', type=click.Path(exists=True))
@click.pass_context
def esri_load_geojson(ctx, filename):
    """Loads the existing geojson for the given endpoint into mongodb"""
    worker = work.Runner.from_file(filename)
    harvester = RESTHarvester(worker.layer)
    harvester.load_to(GEOJSONLoader, worker)


@cli.command('esri-clear-feature-cache', short_help='Clears a given endpoint\'s feature cache')
@click.argument('filename', type=click.Path(exists=True))
@click.pass_context
def esri_clear_feature_cache(ctx, filename):
    """Clears the saved features for a given endpoint, does NOT clear the feature count or id list"""
    worker = work.Runner.from_file(filename)
    harvester = RESTHarvester(worker.layer)
    harvester.clear_feature_cache(all_features=True)


if __name__ == '__main__':
    cli()
