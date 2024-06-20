import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini_pic_wall.settings')
app = Celery('mini_pic_wall')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
