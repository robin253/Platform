#!/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings


# set the default Django settings module for the 'celery' program.
#设置这个环境变量是为了让 Celery 找到 Django 项目
#这条语句必须出现在 Celery 实例创建之前
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dbenvmanager.settings')#dbenvmanager is projectname

#这个app 就是 Celery 实例
app = Celery('dbenvmanager')



app.config_from_object('django.conf:settings')


#Load task modules from all registered Django app configs.

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)  
