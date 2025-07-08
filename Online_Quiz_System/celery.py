'''
import os
#from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Quiz_System.settings')

app = Celery('Online_Quiz_System')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
'''