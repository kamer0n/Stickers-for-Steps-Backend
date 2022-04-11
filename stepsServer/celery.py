import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stepsServer.settings')
from django.conf import settings
from celery.schedules import crontab

from steps.tasks import clearStepsAndSticker, bigTest

from celery import Celery

# Set the default Django settings module for the 'celery' program.


app = Celery('stepsServer', broker='redis://localhost')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, force=True)

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
        'task': 'steps.tasks.clearStepsAndSticker',
        'schedule': crontab(hour=0, minute=0),
        'args': (),
    },
    'run-some-afternoon': {
        'task': 'steps.tasks.bigTest',
        'schedule': crontab(hour=15, minute=8),
        'args': (),
    },
}