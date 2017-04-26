# -*- coding:utf-8 -*-
from django.shortcuts import render

from django.db.models import Q  

from dmlaudit import models
from common import sendwechat
from dmlaudit import constant

import dbause
from django.contrib.auth.decorators import login_required




@login_required(login_url="/")
def dbause_changestatus(request):
    if request.method=="POST":
        pass
    else:
        dbause_information=dbause.dbuse_info() #调用dbause.py的函数
        return render(request, "dmlaudit/dbause.html",dbause_information)

    audit_batch=request.POST['audit_batch']
    batch_status=request.POST['batch_status']  #batch_status=request.POST.get('batch_status','')

    evaluator=request.user.username
    re_modify=models.T_DMLAUDIT_BATCH_INFO.objects.get(audit_batch=audit_batch)#单行查询
    re_modify.batch_status = batch_status
    re_modify.evaluator=evaluator
    if batch_status=='unqualified' or batch_status=='cancel':
        re_modify.execute_status='noexe'   
    re_modify.save()



    #微信
    if  constant.sendwechat_flag==1:#微信开关打开时 发送微信   
        message_content=''
        if batch_status=='unqualified':
            message_content=str(audit_batch)+"批次审核不通过！请线下沟通（审核人："+str(evaluator)+"）"
        elif batch_status=='qualified':
            message_content=str(audit_batch)+"批次审核通过，等待DBA执行（审核人："+str(evaluator)+"）"
        elif batch_status=='cancel':
            message_content=str(audit_batch)+"批次已被取消，请线下沟通（审核人："+str(evaluator)+"）"

        if message_content!='':
            wechat_sender = sendwechat.WeChat()#初始化对象
            msg_dict=wechat_sender.send_messages(message_content)#调用方法发送信息 并返回信息
    else:
        pass

    dbause_information=dbause.dbuse_info() #调用dbause.py的函数
    return render(request, "dmlaudit/dbause.html",dbause_information)
    #return render_to_response('dmlaudit/dbause.html',dbause_information, RequestContext(request))