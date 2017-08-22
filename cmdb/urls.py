#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by liangbaoli on 2017-07-29
"""my_gift URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from views import getdbmeta



urlpatterns = [
    # url(r'^', include('newbee.webui.urls')),
    url(r'^info/$', getdbmeta, name='dbmetainfourl'),
]
