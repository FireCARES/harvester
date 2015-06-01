BROKER_URL = 'amqp://guest:guest@localhost:5672//'

CELERY_IMPORTS = ('harvester.providers.esri', 'harvester.work')

CELERY_RESULT_BACKEND = 'amqp'

CELERY_TRACK_STARTED = True

CELERY_ALWAYS_EAGER = True
