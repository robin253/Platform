# -*- coding: utf-8 -*-
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
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from rest_framework.authtoken import views as restview
from api import views as api_views


"""
save_host_exe_group : 批量添加主机列表到执行组  刘东发

"""


urlpatterns = [
    url(r'^api/token/', restview.obtain_auth_token),
    url(r'^api/', include('newbee.api.urls')),
    url(r'trigger/$', api_views.triggerlist,name='trigger_savehost'),
    url(r'^', include('newbee.webui.urls')),
    url(r'^api/liuyu/$', api_views.testmission,name='liuyu'),
    url(r'save_host_exe_groups/$', api_views.save_host_exe_group,name='save_host_exe'),
    url(r'^api/playbook/$',api_views.playbook,name='playbook'),
    url(r'^api/mission_log/$',api_views.mission_log,name='log'),
    url(r'^api/progress_bar/$',api_views.progress_bar,name='progress_bar'),
    url(r'^api/hostmsgmigrate/$', api_views.hostmsgmigrate,name='liuyu'),
]

