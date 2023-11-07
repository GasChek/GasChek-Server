from __future__ import absolute_import, unicode_literals
import os
from datetime import timedelta
from celery import Celery

# set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaschek_server.settings')

app = Celery('gaschek_server')

# define the default Celery settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# discover tasks in all installed Django apps
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'run-my-task-every-5-seconds': {
        'task': 'gaschek_server.tasks.delete_inactive_models',
        'schedule': timedelta(seconds=5),
    },
}
