# -*- coding: utf-8 -*-

from django.shortcuts import render,redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from django.http import HttpResponseRedirect
from django.db.models import Q
from newbee.models import Role,Exe_group,Host,Mission,Host_exe_group
from vanilla import ListView, CreateView, UpdateView, DeleteView,FormView
from django.http import HttpResponse
from django.core.urlresolvers import reverse_lazy
import json
from django.shortcuts import render_to_response
import pprint

def index(req):
    return render(req,'newbee/index.html',{'username':req.user.username})
    # response = render(req, 'newbee/index.html', {'name':'liangbaoli'})
    # return response



# 刘东发 功能：分页展示主机数据、根据主机名模糊查询、展示执行组列表
# 功能说明：类继承了ListView类所有方法、属性
#最终响应客服端数据说明：如
    # {'host_list': [<Host: Host object>, <Host: Host object>, <Host: Host object>], 当前页对象
    #  'is_paginated': True, 是否有上一页或下一页
    #  'object_list': [<Host: Host object>, <Host: Host object>, <Host: Host object>],当前页对象
    #  'page_obj': <Page 1 of 3>,当前显示为 总页数为3的第一页
    #  'paginator': <django.core.paginator.Paginator object at 0x034A6690>, host 集合对象
    #  'view': <webui.views.HostViewSet object at 0x03155170>}           当前HostViewSet对象【很重要！！！！！！】

class HostViewSet(ListView):
 #覆盖父类的全局变量，只在类第一次加载时赋值，对象直接引用如 对象名.全局变量
    paginate_by = 5                #每页显示记录数
    template_name = 'newbee/host.html' #响应的html

   #构造函数：创建对象时调用；成员变量【当前对象的变量】
    def __init__(self):
        self.model = Host                       #分页数据对象
        self.hostname = ''                      #显示查询条件
        self.exe_groups=Exe_group.objects.all() #显示执行组集合

    #覆盖父类的方法
    def get_queryset(self):

        try:
          # 根据主机名模糊查询
            keyword = self.request.GET['hostname']
            self.hostname=keyword
        except:
            keyword = ''
        if keyword == '':
            # pprint.pprint('if')
            return Host.objects.all()
        else:
            #hostname__contains=keyword 模糊查询；(hostname=keyword 精确查询
            return Host.objects.filter(Q(hostname__contains=keyword))


class RoleViewSet(ListView):
    # Role.objects.all().count()
    model = Role
    template_name = 'newbee/role.html'
    paginate_by = 10

    def get_queryset(self):
        # support search
        try:
            keyword = self.request.GET['keyword']
        except:
            keyword = ''
        if keyword == '':
            return Role.objects.all()
        else:
            return Role.objects.filter(Q(tag__alias=keyword))

class Exe_groupViewSet(ListView):
    # Exe_group.objects.all().count()
    model = Exe_group
    template_name = 'newbee/exe_group.html'
    paginate_by = 10

    def get_queryset(self):
        # support search
        try:
            keyword = self.request.GET['exe_groupname']
            self.inputword=keyword
        except:
            keyword = ''
        if keyword == '':
            return Exe_group.objects.all()
        else:
            return Exe_group.objects.filter(Q(exe_groupname__contains=keyword))

class Host_exe_groupViewSet(ListView):
    # Host_exe_group.objects.all().count()
    model = Host_exe_group
    template_name = 'newbee/host_exe_group.html'
    paginate_by = 10
    hostlist=[]
    exe_groupname=[]
    def get_queryset(self):
        # support search
        try:
            keyword = self.request.GET['id']
            self.exe_groupname=self.request.GET['exe_groupname']
            self.hostlist=Host_exe_group.objects.select_related().filter(exe_groupid=keyword)
        except:
            keyword = ''
        if keyword == '':
            return Host_exe_group.objects.select_related().all()
        else:
            return Host_exe_group.objects.select_related().filter(exe_groupid=keyword)

class MissionViewSet(ListView):
    model = Mission
    template_name = 'newbee/mission.html'
    paginate_by = 10
    #自定义属性
   # hostname = ''                      #显示查询条件

    def get_queryset(self):
        try:
            keyword = self.request.GET['exe_groupname']
            self.inputword = keyword
        except :
            keyword = ''
        if keyword == '':
            return Mission.objects.filter(status=0)
        else:
            return Mission.objects.filter(status=0).filter(Q(exe_groupname__contains=keyword))


class Finished_missionViewSet(ListView):
    model = Mission
    template_name = 'newbee/finished_mission.html'
    paginate_by = 10
    #自定义属性
   # hostname = ''                      #显示查询条件



    def get_queryset(self):

        #获取url参数的方法
        #print self.kwargs
        try:
            keyword = self.request.GET['exe_groupname']
        except:
            keyword = ''
        if keyword == '':
            return Mission.objects.exclude(status=0)
        else:
            return Mission.objects.exclude(status=0).filter(Q(exe_groupname__contains=keyword))
