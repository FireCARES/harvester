# -*- coding: utf-8 -*-
import click
from harvester.esri import ESRIHarvester
from harvester.workers import split_job
import logging
import logging.config

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
@click.option('--cache/--no-cache', default=True, help='Always pull from source (--no-cache) or local filesystem if response is cached')
@click.pass_context
def harvest(ctx, cache):
    """Harvesting-related functions."""
    ctx.obj['CACHE'] = cache


@harvest.command('esri-pull-feature-count', short_help='Gets the count of features for the given ESRI rest endpoint')
@click.argument('url')
@click.pass_context
def esri_pull_feature_count(ctx, url):
    log.info('Total features: %d' % (ESRIHarvester(url, cache_enabled=ctx.obj['CACHE']).get_feature_count(),))


@harvest.command('esri-pull-ids', short_help='Pull the list of objectIds from the ESRI rest endpoint')
@click.argument('url')
@click.pass_context
def esri_pull_ids(ctx, url):
    ids = ESRIHarvester(url, cache_enabled=ctx.obj['CACHE']).get_objectids()
    log.info('%d IDs' % (len(ids['objectIds']), ))


@harvest.command('esri-pull-features', short_help='Enques feature harvesting jobs for a the given ESRI rest endpoint, '
                 'stores features in GeoJSON, projected to EPSG:4326 if necessary, starting '
                 'with ObjectID `start` and ending at ObjectID `end`')
@click.argument('url')
@click.argument('start', default=1)
@click.argument('end', default=100)
@click.argument('job_size', default=100)
@click.pass_context
def esri_pull_features(ctx, url, start, end, job_size):
    harvester = ESRIHarvester(url, cache_enabled=ctx.obj['CACHE'])
    result = split_job(harvester, start, end, job_size).delay()
    log.info('Starting harvest of {0} objectids [{1} - {2}] JOB => {3}'.format(url, start, end, result))


if __name__ == '__main__':
    harvest(obj={})
