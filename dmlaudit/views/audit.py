# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required,permission_required

import cmdb
from dmlaudit import models
from dmlaudit import dmlaudit_oracle
from dmlaudit import dmlaudit_mysql
from dmlaudit import constant
from common import seq_generator,sendwechat,splitor

import os
import sys
import chardet
import datetime




@login_required(login_url="/")
@permission_required('dmlaudit.dmlaudit_access',login_url="/")
def audit(request):
    if request.method=="GET":
        return render(request,'dmlaudit/audit.html')
    
    if request.method=="POST":
        db_type=request.POST.get('db_type','')
        db_name=request.POST.get('db_name','')
        skema=request.POST.get('skema','')
        app_name=request.POST.get('app_name','')
        allsqltext=request.POST.get('allsqltext','')#print type(allsqltext) #unicode
        try:
            onedbinfo=cmdb.models.T_CMDB_DBINFO.objects.get(db_type=db_type,db_name=db_name,skema=skema,app_name=app_name)
        except:#如果结果是多个对象 或者无返回结果，会抛出异常
            audit_info={'errmsg':"无对应数据库信息"}
            return render(request,'dmlaudit/audit.html', audit_info)
        else:
            pass

 
        try:
            filesqltext=request.FILES['filesqltext']
        except:
            pass
        else:
            #print filesqltext.name
            #print type(filesqltext)#django.core.files.uploadedfile.InMemoryUpLoadFile
            list_tmp=[]
            codeflag=0
            for item in filesqltext.chunks():
                #type(item) #str
                code=chardet.detect(item)['encoding']
                #字符集一般是utf-8 GB2312 windows1521 ascii等
                #print sys.getdefaultencoding()
                if not code.upper().startswith('UTF-8'):
                    codeflag=1
                    break
                else:
                    list_tmp.append(item.decode(code))#转为unicode

            if codeflag==0:
                str_tmp=' '.join(list_tmp) #unicode
                allsqltext=str_tmp
            else:
                audit_info = {
                'errmsg':"上传文件非UTF-8编码或内容为空",
                'db_type':db_type,
                'db_name':db_name,
                'skema':skema,
                'app_name':app_name
                             }
                return render(request,'dmlaudit/audit.html', audit_info)
        
        #如果输入框文本为空
        if not allsqltext:
            audit_info = {
            'errmsg':"审核文本为空",
            'db_type':db_type,
            'db_name':db_name,
            'skema':skema,
            'app_name':app_name
                        }
            return render(request,'dmlaudit/audit.html', audit_info)


    list_auditresult=[]
    try:
        if db_type=='oracle':
            auditobject=dmlaudit_oracle.DmlAudit(onedbinfo.username,onedbinfo.password,onedbinfo.ipadress,\
            onedbinfo.port,onedbinfo.servicename)
        elif db_type=='mysql':
            auditobject=dmlaudit_mysql.DmlAudit(onedbinfo.username,onedbinfo.password,onedbinfo.ipadress,\
            onedbinfo.port,onedbinfo.skema)
    except:
        audit_info = {
        'errmsg':"数据库连接失败",
        'allsqltext':allsqltext
                     }
        return render(request,'dmlaudit/audit.html', audit_info)
    else:
        lexerSplitor = splitor.LexerSplitor()
        sqlnum=1
        for onesql in lexerSplitor.split(allsqltext):
            #print onesql
            tmp_dict=auditobject.audit(onesql)
            if tmp_dict is None:  #如果是纯注释语句 返回空 一般是最后无用的注释
                continue
            tmp_dict['sqlnum']=sqlnum#批次sql条数的编号
            list_auditresult.append(tmp_dict)
            sqlnum=sqlnum+1

        auditobject.close_commit()


    audit_user=request.user.username
    audit_batch=seq_generator.dmlaudit_batch()#生成批次号
    sqlamount=len(list_auditresult) #记录该批次的sql条数

    if sqlamount==0:#只有纯注释语句
        audit_info = {
        'errmsg':"请不要提交纯注释语句"}
        return render(request,'dmlaudit/audit.html', audit_info)



    #批次状态 取所有sql的最差状态
    list_batch_status=[]
    for auditresult in list_auditresult:
        list_batch_status.append(auditresult['audit_status'])

    if list_batch_status.count("unqualified")>0:
        batch_status="unqualified"
        execute_status='noexe'#不可以执行的
    elif list_batch_status.count("semi-qualified")>0:
        batch_status="semi-qualified"
        execute_status='init'
    else:
        batch_status="qualified"
        execute_status='init'



    #记录到数据模型 T_DMLAUDIT_BATCH_INFO 中
    model_batch_info_insert=models.T_DMLAUDIT_BATCH_INFO(audit_user=audit_user,audit_batch=audit_batch,app_name=app_name,\
        db_type=db_type,allsqltext=allsqltext,sqlamount=sqlamount,batch_status=batch_status,execute_status=execute_status)
    model_batch_info_insert.save()

    #记录到数据模型 T_DMLAUDIT_BATCH_DETAIL 中
    for auditresult in list_auditresult:
        #auditresult是每句sql审核返回的字典 有如下的key
        #['sqltext','grammar','gra_failreason','sqlplan','rowaffact','audit_status','sqltype','plan_passflag','sqlnum']
        model_batch_detail_insert =models.T_DMLAUDIT_BATCH_DETAIL(audit_batch=model_batch_info_insert,**auditresult)
        model_batch_detail_insert.save()



    #微信
    if  constant.sendwechat_flag==1:#微信开关打开时 发送微信
        wechat_sender = sendwechat.WeChat()#初始化对象

        message_content=''
        if batch_status=='qualified':
            message_content=str(audit_batch)+"批次审核结果：《通过》，请处理（提交人："+str(audit_user)+"）"
        elif batch_status=='semi-qualified':
            message_content=str(audit_batch)+"批次审核结果：《待DBA评估》，请处理（提交人："+str(audit_user)+"）"
        else:
            pass
        if message_content!='':
            msg_dict=wechat_sender.send_messages(message_content)#调用方法发送信息 并返回信息
    else:
        pass

    audit_info = {
        'audit_user': audit_user,
        'audit_batch': audit_batch,
        'app_name': app_name,
        'db_type': db_type,
        'sqlamount': sqlamount,
        'batch_status': batch_status,
        'execute_status': execute_status,
        'list_auditresult': list_auditresult,
        'db_name':db_name,
        'skema':skema,
        'allsqltext':allsqltext
    }
    # 返回到页面展示 (不要查库了 直接将审核结果的列表、变量返回)
    return render(request, 'dmlaudit/audit.html', audit_info)



