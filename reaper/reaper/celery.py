from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from reaper.settings import BACKEND,BROKER
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reaper.settings')  # 设置django环境

# 若不配置backend和broker，则默认使用rebbitmq作为消息中间件
app = Celery('reaper',backend=BACKEND,broker=BROKER)

app.config_from_object('django.conf:settings', namespace='CELERY') #  使用CELERY_ 作为前缀，在settings中写配置


# 使用这句，则在task中就不需要根据相对路径导入celery对象了，只需要导入shared_task
app.autodiscover_tasks(lambda :settings.INSTALLED_APPS)

