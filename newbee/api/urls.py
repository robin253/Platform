# -*- coding: utf-8 -*-
from django.conf.urls import url
from newbee.api import views
from rest_framework import routers

import pprint
#可以使用webui来访问这些接口做数据操作（增删改查）
router = routers.DefaultRouter()

router.register(r'exe_group', views.Exe_groupViewSet)
router.register(r'host_exe_group', views.Host_exe_groupViewSet)
router.register(r'mission', views.MissionViewSet)
router.register(r'role', views.RoleViewSet)

urlpatterns = router.urls


