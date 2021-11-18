import os
from django.conf import settings
from celery.schedules import crontab

from steps.models import Steps

from celery import Celery, shared_task

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stepsServer.settings')


app = Celery('steps')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(settings.INSTALLED_APPS)


app.conf.beat_schedule = {
    # Executes every day at  12:30 pm.
    'run-every-afternoon': {
        'task': 'clearStepsAndSticker',
        'schedule': crontab(hour=1, minute=3),
        'args': (),
    },
}

