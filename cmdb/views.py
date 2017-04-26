#!/bin/env python
# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
import json
import models
#import datetime




#根据db_type获取db_name
def getdatabase(request):
    db_type = request.GET['db_type']
    re_queryset=models.T_CMDB_DBINFO.objects.filter(db_type=db_type).values('db_name').distinct()
    list_db_name=[]
    for item in re_queryset:
        #item是字典
        list_db_name.append(item)

    #json_data=serializers.serialize("json", re_queryset)  #re_queryset不要有 .values('db_name')
    #return HttpResponse(json_data)

    return HttpResponse(json.dumps(list_db_name))
    #http://localhost:8000/cmdb/getdatabase?db_type=oracle

# 根据db_name获取skema
def getschema(request):
    db_name = request.GET['db_name']
    re_queryset=models.T_CMDB_DBINFO.objects.filter(db_name=db_name).values('skema').distinct()

    list_skema=[]
    for item in re_queryset:
        list_skema.append(item)

    return HttpResponse(json.dumps(list_skema))
    #http://localhost:8000/cmdb/getschema?db_name=test



#"db_name","skema","app_name"  唯一约束 根据db_name skema获取app_name
def getapp(request):
    #print datetime.datetime.now()
    db_name = request.GET['db_name']
    skema = request.GET['skema']
    re_queryset=models.T_CMDB_DBINFO.objects.filter(db_name=db_name,skema=skema).values('app_name').distinct()

    list_app_name=[]
    for item in re_queryset:
        list_app_name.append(item)

    return HttpResponse(json.dumps(list_app_name))
    #http://localhost:8000/cmdb/getapp?db_name=test&skema=xulijia


