BROKER_URL = 'amqp://guest:guest@localhost:5672//'

CELERY_IMPORTS = ('harvester.workers',)

CELERY_RESULT_BACKEND = 'amqp'
