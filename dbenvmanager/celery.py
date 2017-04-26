#!/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings


# set the default Django settings module for the 'celery' program.
#设置这个环境变量是为了让 Celery 找到 Django 项目
#这条语句必须出现在 Celery 实例创建之前
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dbenvmanager.settings')#projectname

#这个app 就是 Celery 实例
app = Celery('dbenvmanager')


# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
#app.config_from_object('django.conf:settings', namespace='CELERY') 
app.config_from_object('django.conf:settings')  

# Load task modules from all registered Django app configs.
#app.autodiscover_tasks()
#加上这一句后，Celery 会自动发现 Django 各个应用中tasks.py文件 并找到被装饰的函数
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)  
