# -*- coding: UTF-8 -*-
from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app  #是导入当前路径下celery的app!
