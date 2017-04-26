#!/bin/env python
# -*- coding: UTF-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
import sqlstat

import tasks
from models import InefficientSql
import cmdb



def getpageinfo():
    re_queryset=cmdb.models.T_CMDB_DBINFO.objects.values('db_name','skema').distinct()

    list_db_name=[]
    list_skema=[]
    for item in re_queryset:
        if item['db_name'] not in list_db_name:
            list_db_name.append(item['db_name'])
        if item['skema'] not in list_skema:
            list_skema.append(item['skema'])
    dict_re={'list_db_name':list_db_name,'list_skema':list_skema}
    return dict_re

#page view
def sqlplanchange(request):
    if request.method=='GET':
        dict_pageinfo=getpageinfo()
        return render(request, 'performance/sqlplanchange.html',dict_pageinfo)

    if request.method=="POST":
        db_name=request.POST['db_name']
        skema=request.POST['skema']
        re_queryset=cmdb.models.T_CMDB_DBINFO.objects.filter(db_name=db_name,skema=skema).\
        values('ipadress','port','servicename','dbausername','dbapassword','privilege_flag','appuser').distinct()

        if re_queryset[0]['privilege_flag']=='N':
            parsing_shema_name=skema
        else:
            parsing_shema_name=re_queryset[0]['appuser']
 

        dict_tmp={"ipadress":re_queryset[0]['ipadress'],
                  "port":re_queryset[0]['port'],
                  "servicename":re_queryset[0]['servicename'],
                  "dbausername":re_queryset[0]['dbausername'],
                  "dbapassword":re_queryset[0]['dbapassword'],
                  'parsing_shema_name':parsing_shema_name
                  }
        #print dict_tmp

        list_planchange=sqlstat.planchange(**dict_tmp)
        #print list_planchange
        dict_pageinfo=getpageinfo()
        dict_pageinfo['list_planchange']=list_planchange
        return render(request, 'performance/sqlplanchange.html',dict_pageinfo)



#page view
def sqlinefficient(request):
    if request.method=="GET":
        dict_pageinfo=getpageinfo()
        return render(request, 'performance/sqlinefficient.html',dict_pageinfo)

    if request.method=="POST":     
          
        db_name=request.POST['db_name']
        skema=request.POST['skema']
        #tasks.sendwe.delay('11')
        if request.POST.has_key('check'):
            #查询模型数据并显示
            re_queryset=InefficientSql.objects.filter(skema=skema)
            dict_pageinfo=getpageinfo()
            dict_pageinfo['list_inefficient']=re_queryset
            return render(request, 'performance/sqlinefficient.html',dict_pageinfo)

        if request.POST.has_key('refresh'):
            #更新模型数据并显示
            re_queryset=cmdb.models.T_CMDB_DBINFO.objects.filter(db_name=db_name,skema=skema).\
            values('ipadress','port','servicename','dbausername','dbapassword','privilege_flag','appuser').distinct()

            if re_queryset[0]['privilege_flag']=='N':
                parsing_shema_name=skema
            else:
                parsing_shema_name=re_queryset[0]['appuser']

            dict_tmp={"ipadress":re_queryset[0]['ipadress'],
                  "port":re_queryset[0]['port'],
                  "servicename":re_queryset[0]['servicename'],
                  "dbausername":re_queryset[0]['dbausername'],
                  "dbapassword":re_queryset[0]['dbapassword'],
                  'parsing_shema_name':parsing_shema_name
                  }

            list_inefficient=sqlstat.inefficient(**dict_tmp)

            if isinstance(list_inefficient,str):
                wrongmessge=list_inefficient
                return render(request, 'performance/sqlinefficient.html',wrongmessge)
            else: 
                querysetlist=[]
                for item in list_inefficient:
                    re=InefficientSql.objects.filter(skema=skema,inst_id=item['inst_id'],sql_id=item['sql_id'])
                    if re:
                        pass
                    else:
                        item['skema']=skema
                        mysave=InefficientSql(**item)
                        mysave.save()

                re_queryset=InefficientSql.objects.filter(skema=skema)
                dict_pageinfo=getpageinfo()
                dict_pageinfo['list_inefficient']=re_queryset
                return render(request, 'performance/sqlinefficient.html',dict_pageinfo)



def sqlinefficient_changestatus(request):
    if request.method=="POST":     
        info=request.POST['skema.sql_id']
        status=request.POST['status']
        skema=info.split('.')[0]
        sql_id=info.split('.')[1]
        #更新状态 两个实例都有这个sql那么一起更新
        re_modify=InefficientSql.objects.filter(skema=skema,sql_id=sql_id)
        for obj in re_modify:
            obj.status=status
            obj.save()

        
        re_queryset=InefficientSql.objects.filter(skema=skema)
        dict_pageinfo=getpageinfo()
        dict_pageinfo['list_inefficient']=re_queryset
        return render(request, 'performance/sqlinefficient.html',dict_pageinfo)

def sqlanalysis(request):
    return render(request, 'performance/sqlanalysis.html')