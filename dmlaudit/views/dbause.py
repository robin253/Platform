# -*- coding:utf-8 -*-
from django.shortcuts import render

from dmlaudit import models

from django.db.models import Q  
from django.contrib.auth.decorators import login_required,permission_required



def dbuse_info():
    #待评估或执行的语句
    re_tmp=models.T_DMLAUDIT_BATCH_INFO.objects.filter(Q(batch_status='qualified')|Q(batch_status='semi-qualified'))
    #待处理状态的
    re_evaluate=re_tmp.filter(Q(execute_status='init')|Q(execute_status='doing')).order_by("-audit_batch")
    todealnum=len(re_evaluate)
    #已执行成功的
    re_suc=re_tmp.filter(execute_status='suc').order_by("-audit_batch")[:10]
    #执行失败的
    re_fail=re_tmp.filter(execute_status='fail').order_by("-audit_batch")[:10]

    dbause_info = {
        're_suc':re_suc,
        're_evaluate':re_evaluate,
        're_fail':re_fail,
        'todealnum':todealnum

    }
    return dbause_info


@login_required(login_url="/")
@permission_required('dmlaudit.dmldbause_access',login_url="/")
def dbause(request):
    dbause_information=dbuse_info() #调用函数
    return render(request,'dmlaudit/dbause.html',dbause_information)
