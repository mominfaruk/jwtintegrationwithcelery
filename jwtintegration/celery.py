import imp
from django.conf import settings

import os

from pytz import timezone
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jwtintegration.settings')

app=Celery('jwtintegration')
app.conf.enable_utc=False

app.conf.update(timezone='Asia/Dhaka')

app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')