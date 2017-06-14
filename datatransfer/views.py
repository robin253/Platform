#!/bin/env python
# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import HttpResponse

import logging
import cmdb
import oracledump
import json
import models

logger = logging.getLogger(__name__)#用logging.getLogger(name)方法进行初始化，获得一个记录器的实体
                                    # __name__是基于每个模块名的用点号相连的名字，点号之前的是点号之后的父模块
                                    #通过层次，子层次的消息可以把消息发送给自己的父层次


#获取expdp ajax传输的信息
def expdpforminfo(request):
    db_name=request.GET.get('db_name','')
    skema=request.GET.get('skema','')
    re_queryset=cmdb.models.T_CMDB_DBINFO.objects.filter(db_type='oracle',db_name=db_name,skema=skema)
    ipadress=re_queryset[0].ipadress
    port=re_queryset[0].port
    servicename=re_queryset[0].servicename
    dbausername=re_queryset[0].dbausername
    dbapassword=re_queryset[0].dbapassword
    directory=re_queryset[0].directory
    sysuser=re_queryset[0].sysuser
    syspassword=re_queryset[0].syspassword


    tables=request.GET.get('tables','').upper()
    list_tmp=tables.split(",")
    list_tables=[]
    for table in list_tmp:
        list_tables.append(skema+"."+table)
    tables=','.join(list_tables)
            
    content=request.GET.get('content','')
    parallel=request.GET.get('parallel','')   

    statistics=request.GET.get('statistics','')  
    index=request.GET.get('index','') 
    constraint=request.GET.get('constraint','')   
    grant=request.GET.get('grant','')
    additional=request.GET.get('additional','')  
    tmpstr=""
    #print "=====",statistics,index,constraint,grant
    if statistics or index or constraint or grant:
        tmpstr="exclude="
        if statistics:
            tmpstr=tmpstr+statistics+","
        if index:
            tmpstr=tmpstr+index+","
        if constraint:
            tmpstr=tmpstr+constraint+","
        if grant:
            tmpstr=tmpstr+grant+","
    additional=tmpstr[0:-1]+" "+additional
    #print tables,content,parallel,additional
    dict_return={}
    for i in ['db_name','skema','ipadress','port','servicename','dbausername','dbapassword',\
    'directory','sysuser','syspassword','tables','content','parallel','additional']:
        dict_return[i]=locals()[i]
    return dict_return


#获取impdp ajax传输的信息
def impdpforminfo(request):
    db_name=request.GET.get('db_name','')
    skema=request.GET.get('skema','')
    re_queryset=cmdb.models.T_CMDB_DBINFO.objects.filter(db_type='oracle',db_name=db_name,skema=skema)
    ipadress=re_queryset[0].ipadress
    port=re_queryset[0].port
    servicename=re_queryset[0].servicename
    dbausername=re_queryset[0].dbausername
    dbapassword=re_queryset[0].dbapassword
    directory=re_queryset[0].directory
    sysuser=re_queryset[0].sysuser
    syspassword=re_queryset[0].syspassword

    table_exists_action=request.GET.get('table_exists_action','')
    remap_table=request.GET.get('remap_table','')  

    expdp_job_name=request.GET.get('job_name','')  

    re_job_name=models.T_DATATRANSFER_EXPDP.objects.get(job_name=expdp_job_name)

    expdp_skema=re_job_name.skema
    tables=re_job_name.tables
    expdp_tablespace=re_job_name.tablespace
    expdp_dumpfilepath=re_job_name.dumpfilepath
    expdp_parallel=re_job_name.parallel

    dict_return={}
    for i in ['db_name','skema','ipadress','port','servicename','dbausername','dbapassword',\
    'directory','sysuser','syspassword','table_exists_action','remap_table','expdp_job_name','expdp_skema',\
    'tables','expdp_tablespace','expdp_dumpfilepath','expdp_parallel']:
        dict_return[i]=locals()[i]
    return dict_return


#view func
def oradump_expdpcommand(request):
    tmp_dict=expdpforminfo(request)
    del tmp_dict['db_name'] 
    #print tmp_dict

    #如果没有输入表名
    if tmp_dict['tables']==tmp_dict['skema']+".":
        return HttpResponse(json.dumps([{'inf':"错误！没有输入任何表名！"},{'inf':"N/A"},{'inf':"N/A"}]))

    try:
        obj_expdp=oracledump.expdp_process(**tmp_dict)
    except:
        return HttpResponse(json.dumps([{'inf':"获取信息失败"},{'inf':"获取信息失败"},{'inf':"获取信息失败"}]))

    else:
        expdpcommand=obj_expdp.get_expdpcommand()[1]
        segments_bytes=obj_expdp.get_segments_bytes()
        tablespace=obj_expdp.get_tablespace()
        tablespaceshow="表空间:\n"+tablespace['tab']+"\n索引表空间:\n"+tablespace['idx']
        difftables=obj_expdp.check_tables()
        dumpfilepath=obj_expdp.get_dumpfilepath()
        obj_expdp.close() 
        errinfo=""
        if difftables=="error":
            errinfo="表检测异常"
        if difftables!="error" and difftables!="":
            errinfo=difftables+"表不存在"
        if dumpfilepath=='error':
            errinfo="找不到directory "+tmp_dict['directory']+"对应的路径"
        if segments_bytes=='error':
            errinfo="数据量预估异常"
        if  errinfo!="":
            return HttpResponse(json.dumps([{'inf':errinfo},{'inf':"N/A"},{'inf':"N/A"}]))
        else:
            return HttpResponse(json.dumps([{'inf':expdpcommand},{'inf':str(segments_bytes)+"M"},{'inf':str(tablespaceshow)}]))



#view func
def oradump_expdp(request):
    if request.GET.keys()==[]:
        re_queryset=cmdb.models.T_CMDB_DBINFO.objects.filter(db_type='oracle').values('db_name').distinct()
        list_db_name=[]
        for item in re_queryset:
            list_db_name.append(item['db_name'])
        return render(request, 'datatransfer/trans_oradump_expdp.html',{'list_db_name':list_db_name})
    else:
        tmp_dict=expdpforminfo(request)
        db_name=tmp_dict['db_name'] 
        del tmp_dict['db_name'] 
        try:
            obj_expdp=oracledump.expdp_process(**tmp_dict)
        except:
            return HttpResponse(json.dumps([{'inf':"发起失败"},{'inf':"N/A"}]))
        else:
            job_name,expdpcommand=obj_expdp.get_expdpcommand()
            dumpfilepath=obj_expdp.get_dumpfilepath()
            segments_bytes=obj_expdp.get_segments_bytes()
            tablespace=obj_expdp.get_tablespace()
            #信息入库
            dict_dbinsert={
             'launch_user':request.user.username,
             'db_name':db_name,
             'skema':tmp_dict['skema'],
             'job_name':job_name,
             'tables':tmp_dict['tables'],
             'tablespace':tablespace,
             'segments_bytes':segments_bytes,
             'directory':tmp_dict['directory'],
             'dumpfilepath':dumpfilepath,
             'parallel':tmp_dict['parallel'],
             'expdpcommand':expdpcommand,
             'logfile':'已发起',
             'status':'init'}
            model_expdp_insert=models.T_DATATRANSFER_EXPDP(**dict_dbinsert)
            model_expdp_insert.save()

            status,logfile=obj_expdp.start_expdp(job_name,expdpcommand)
            obj_expdp.close()

            #更新库
            model_expdp_update=models.T_DATATRANSFER_EXPDP.objects.get(job_name=job_name)
            model_expdp_update.logfile=logfile
            model_expdp_update.status=status
            model_expdp_update.save()

            return HttpResponse(json.dumps([{'inf':status},{'inf':logfile}]))








        



        



#view func
def oradump_impdpcommand(request):
    tmp_dict=impdpforminfo(request)
    del tmp_dict['db_name'] 
    #print tmp_dict

    try:
        obj_impdp=oracledump.impdp_process(**tmp_dict)
    except:
        return HttpResponse(json.dumps([{'inf':"获取信息失败"},{'inf':"获取信息失败"}]))

    else:
        impdpcommand=obj_impdp.get_impdpcommand()[1]
        tableexists=obj_impdp.check_tables()
        dumpfilepath=obj_impdp.get_dumpfilepath()
        obj_impdp.close() 
        errinfo=""
        if tableexists=="error":
            errinfo="表检测异常"
        if tableexists!="error" and tableexists!="":
            errinfo="目标端"+tableexists+"表不存在"
        if tableexists=="":
            errinfo="目标端表都存在"
        if dumpfilepath=='error':
            errinfo="找不到directory "+tmp_dict['directory']+"对应的路径"
        return HttpResponse(json.dumps([{'inf':impdpcommand},{'inf':errinfo}]))


    

#view func
def  oradump_impdp(request):
    if request.GET.keys()==[]:
        re_queryset=cmdb.models.T_CMDB_DBINFO.objects.filter(db_type='oracle').values('db_name').distinct()
        list_db_name=[]
        for item in re_queryset:
            list_db_name.append(item['db_name'])

        re_job_name=models.T_DATATRANSFER_EXPDP.objects.filter(status="suc").values("job_name").distinct()
        list_job_name=[]
        for item in re_job_name:
            list_job_name.append(item['job_name'])
        return render(request, 'datatransfer/trans_oradump_impdp.html',{'list_db_name':list_db_name,"list_job_name":list_job_name})

    else:

        tmp_dict=impdpforminfo(request)
        db_name=tmp_dict['db_name'] 
        del tmp_dict['db_name'] 
        try:
            obj_impdp=oracledump.impdp_process(**tmp_dict)
        except:
            return HttpResponse(json.dumps([{'inf':"发起失败"},{'inf':"N/A"}]))
        else:
            impdp_job_name,impdpcommand=obj_impdp.get_impdpcommand()
            #信息入库
            status,logfile=obj_impdp.start_impdp(impdp_job_name,impdpcommand)
            obj_impdp.close()
            #print status,logfile
            #更新库
            return HttpResponse(json.dumps([{'inf':status},{'inf':logfile}]))


def trans_oraldr(request):
    return render(request, 'datatransfer/trans_oraldr.html')


def trans_mysqldump(request):
    return render(request, 'datatransfer/trans_mysqldump.html')

def logicalbackup(request):
    
    return render(request, 'datatransfer/logicalbackup.html')

def hisdata(request):
    
    return render(request, 'datatransfer/hisdata.html')

