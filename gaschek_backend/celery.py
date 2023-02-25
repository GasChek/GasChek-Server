import os
from celery import Celery

# set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaschek_backend.settings')

app = Celery('gaschek_backend')

# define the default Celery settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# discover tasks in all installed Django apps
app.autodiscover_tasks()
