import os

from celery import Celery
from django.conf import settings
from hirefire.procs.celery import CeleryProc

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "twitter_chatbot.settings")

app = Celery("twitter_chatbot")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


class WorkerProc(CeleryProc):
    name = 'celery'
    queues = ['celery']
    app = app
    inspect_statuses = ['active']
    simple_queues = True
