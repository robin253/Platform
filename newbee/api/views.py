# -*- coding: utf-8 -*-
# Create your views here.
from __future__ import division
from rest_framework import viewsets
from rest_framework import filters as source_filter
import rest_framework_filters as filters
from rest_framework_filters.backends import DjangoFilterBackend
from serializers import *
from newbee.models import *
from filter import *
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
#from savehost import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ansibles.playbook import *
import json


#from host_migerate import *

from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser


#from host_migerate import *



class SearchViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    filter_backends = (DjangoFilterBackend,source_filter.SearchFilter)

    def perform_create(self, serializer):
        print 'hahha++++++++++++++++++++++hahah'
        return super(SearchViewSet, self).perform_create(serializer)

class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    filter_backends = (DjangoFilterBackend,)

    def perform_create(self, serializer):
        return super(BaseViewSet, self).perform_create(serializer)


# FunctiongroupViewSet类
# http_method_names允许的http_method_names，不写默认为允许所有方法
# filter_fields 允许作为查询过滤的字段
#以下几个 **ViewSet类都差不多类似

class FunctiongroupViewSet(BaseViewSet):
    http_method_names = ['post', 'get', 'put', 'patch']
    queryset = Functiongroup.objects.all()
    serializer_class = Functiongroupserializers
    filter_fields = ('fun_groupname',)

class HostViewSet(BaseViewSet):
    http_method_names = ['post', 'get', 'put', 'patch']
    queryset = Host.objects.all()
    serializer_class = Hostserializers
    filter_fields = ('hostname','ip','port','status','host_var')

class RoleViewSet(BaseViewSet):
    http_method_names = ['post', 'get', 'put', 'patch']
    queryset = Role.objects.all()
    serializer_class = Roleserializers
    filter_fields = ('id',)

class Exe_groupViewSet(BaseViewSet):
    http_method_names = ['post', 'get', 'put', 'patch','delete']
    queryset = Exe_group.objects.all()
    serializer_class = Exe_groupserializers
    filter_fields = ('id','exe_groupname',)


    def list(self, request, *args, **kwargs):
        return super(Exe_groupViewSet, self).list(request, args, kwargs)

    def create(self, request, *args, **kwargs):
        res = super(Exe_groupViewSet,self).create(request,args,kwargs)
        return res

    def update(self, request, *args, **kwargs):
        print "+++++++++++++++++++++++++++++++++++"
        return super(Exe_groupViewSet, self).update(request,args,kwargs)

    def retrieve(self, request, *args, **kwargs):
        print "==============================="
        return super(Exe_groupViewSet, self).retrieve(request,args, kwargs)


class Host_exe_groupViewSet(BaseViewSet):
    http_method_names = ['post', 'get', 'put', 'patch','delete']
    queryset = Host_exe_group.objects.all()
    serializer_class = Host_exe_groupserializers
    filter_fields = ('hostid','exe_groupid',)

class MissionViewSet(BaseViewSet):
    http_method_names = ['post', 'get', 'put', 'patch','delete']
    queryset = Mission.objects.all()
    serializer_class = Missionserializers
    filter_fields = ('id','exe_groupname',)

class ExeuserViewSet(BaseViewSet):
    http_method_names = ['post', 'get', 'put', 'patch','delete']
    queryset = Exeuser.objects.all()
    serializer_class = Exeuserserializers
    filter_fields = ('id','Exeuser',)

@api_view(['GET', 'POST'])
def triggerlist(request):
      if request.method == 'GET':
           #savehost()
           response = HttpResponse("save host successfully")
      return response



@csrf_exempt
def testmission(request):
      if request.method == 'POST':
                id = request.body
                if id == '1':

                    response = HttpResponse('hello liu yu')
                else:
                    response = HttpResponse(id)
      return response
#author Jane.Hoo
#功能：实现将zabbix数据入到自动化平台库中
import pprint
import os
import time
from hostmigerate import  *
def hostmsgmigrate(request):
      if request.method == 'POST':
                db_msg = request.body
                v_cur_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                v_zabbix_db_msg=db_msg.split('=')[0]
                v_ansibleui_db_msg=db_msg.split('=')[1]
                v_result=test(v_cur_time,v_zabbix_db_msg,v_ansibleui_db_msg)

                if v_result == 'OK':
                    response = HttpResponse('监控平台中主机数据已成功迁移至自动化平台！')
                elif v_result == 'DB NOT OK':
                    response = HttpResponse('数据库连接失败，请检查数据库配置！')
                else:
                    response = HttpResponse('监控平台中主机数据迁移失败！')
      return response

import pprint
@api_view(['GET', 'POST'])
# 刘东发 功能：批量添加主机列表到执行组
# 请求参数：
#       hostids ：主机id集合字符串。如 1,2,3
#       exe_groupid：执行组id 。如 1
# 主要步骤说明：
# 批量添加通过 django.db.models 的 bulk_create(models,count) 方法实现
# 其中 models 是Host_exe_group对象集合列表，count 集合个数
# 创建Host_exe_group对象方法：如 Host_exe_group(hostid=1,exe_groupid=2)
# 有因为 Host_exe_group 对象在api.models 体现外键关系即 主表中有的 从表中才可以有，即hostid、exe_groupid 分别代表Host一个实例、Exe_group一个实例
#因此 创建Host_exe_group对象方法，应该是=Host_exe_group(hostid=Host(id=hostid),exe_groupid=Exe_group(id=exe_groupid))

def save_host_exe_group(request):
      try:
          exe_groupid=request.GET['exe_groupid']
          hostids=str(request.GET['hostids']).split(',')
          host_exe_group_objects=[]
          for hostid in hostids:
               host_exe_group_object=Host_exe_group(hostid=Host(id=hostid),exe_groupid=Exe_group(id=exe_groupid))
               host_exe_group_objects.append(host_exe_group_object)
          Host_exe_group.objects.bulk_create(host_exe_group_objects,len(hostids))
          response = HttpResponse("主机列表添加到执行组 成功。")
      except:
             response = HttpResponse("主机列表添加到执行组 失败！！")
      pprint.pprint(response)
      return response


@csrf_exempt
#任务执行
def playbook(request):
    if request.method == 'POST':
        data = eval(request.body)
        id = data['id']
        role = data['rolename']
        exe_group = data['exe_groupname']

        try:
            runner = MyRun()
            runner.run(id,role,exe_group)
            result = runner.get_results(id)
            rlt = json.loads(result)
            #pprint.pprint(result)
            status = 1
            for key,value in  rlt.iteritems():
                if rlt[key]['unreachable']>0 or rlt[key]['failures']>0:
                    status = 2
                else:
                    status = 1
        except Exception as err:
            status = 2
            print '----------------------err----------------------'
            print err
            result = json.dumps({'err':'we get a error'})
        Mission.objects.filter(id=id).update(status= status )
        return HttpResponse(result,content_type='application/json')


@csrf_exempt
# 日志显示
def mission_log(request):
        if request.method == 'POST':
                data = json.loads(request.body)
                #pprint.pprint(request.body)
                id = data["id"]
                path = '/var/log/ansible/'+id
                with open(path,"r") as fd:

                    jdata = fd.read()
        return HttpResponse(jdata)


from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser



#author:fan xinlei
#功能：处理进度条
#步骤1.通过取role表中的某个role的总步数total_step_data
#2.然后取num表中目前执行过程中的步数now_step_data
#3.通过执行进度百分比progress_percent=now_step_data/total_step_data
# 返回结果：百分比
@api_view(['GET'])
def progress_bar(request):
        if request.method == 'GET':
                role_name = request.GET['rolename']
                missionid = request.GET['id']
                try:
                     numlist = Num.objects.values("num").filter(id=missionid)
                     rolelist = Role.objects.values("stepnum").filter(rolename=role_name)
                     numdata = json.dumps(numlist[0])
                     roledata = json.dumps(rolelist[0])
                     now_step_data = json.loads(numdata)['num']
                     total_step_data = json.loads(roledata)['stepnum']
                     if(now_step_data>total_step_data):
                           progress_percent = 500
                     else:
                           progress_percent = round(now_step_data/total_step_data,2)
                except:
                     progress_percent = 500

                # progress_percent=now_step_data/total_step_data
                return  HttpResponse(progress_percent)

