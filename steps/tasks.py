from celery import shared_task
from celery import Celery
from celery.schedules import crontab

from models import Steps

app = Celery()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    sender.add_periodic_task(
        crontab(minute=24, hour=1),
        clearStepsAndSticker.s(),
    )


@shared_task()
def clearStepsAndSticker():
    for steps in Steps.objects.all():
        steps.steps = 0
        steps.stickers_received = 0
        steps.save()
