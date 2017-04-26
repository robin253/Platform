# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# -*- coding:utf-8 -*-
from django.shortcuts import render

import datetime
from ddlaudit import models
import django.contrib.auth.models  # User Group




@login_required(login_url="/")
def checkresult(request):
    #提交人 
    list_audit_user=django.contrib.auth.models.User.objects.values('username').distinct()
    #print list_audit_user

    #审核人  执行人 evaluator   DBA
    list_evaluator=[]
    groupinfo=django.contrib.auth.models.Group.objects.filter(name="DBA")
    for item in groupinfo:
        userinfo=item.user_set.all()
        for item2 in userinfo:
            list_evaluator.append(item2.username)


    #print list_evaluator
    returninfo={
                'list_audit_user': list_audit_user ,
                'list_evaluator':list_evaluator
               }



    if request.method=="POST":

        error_batch=False
        if request.POST.has_key('batchcheck'):
            audit_batch=request.POST['audit_batch']
            #print request.POST.keys()
            try:
                audit_detail=models.T_DDLAUDIT_BATCH_INFO.objects.get(audit_batch=audit_batch)
                re_detail=audit_detail.t_ddlaudit_batch_detail_set.all().order_by('sqlnum') 
                #关联查询 注意大小写是默认的方法   查询关联表数据 re_detail[0].audit_batch.audit_user
            except:
                error_batch=True
            else:
                pass


        elif request.POST.has_key('optioncheck'): 
            #print request.POST.keys()
            batch_status=request.POST['batch_status']
            db_type=request.POST['db_type']
            order_date_from=request.POST['order_date_from']
            order_date_to=request.POST['order_date_to']
            audit_user=request.POST['audit_user']
            evaluator=request.POST['evaluator']
            execute_status=request.POST['execute_status']

            #默认查询2天
            timeformat = '%d/%m/%Y'
            today_value=datetime.datetime.now()
            twobefore_value=today_value+datetime.timedelta(days=-1)
            today = today_value.strftime(timeformat)
            twobefore = twobefore_value.strftime(timeformat)

            if order_date_from == '':
                order_date_from=twobefore
            if order_date_to == '':
                order_date_to=today



            
            day_from=order_date_from.split('/')[0]
            month_from=order_date_from.split('/')[1]
            year_from=order_date_from.split('/')[2]
            release_date_from=year_from+month_from+day_from

            day_to=order_date_to.split('/')[0]
            month_to=order_date_to.split('/')[1]
            year_to=order_date_to.split('/')[2]
            release_date_to=year_to+month_to+day_to

            audit_detail=models.T_DDLAUDIT_BATCH_INFO.objects.filter(release_date__range=(release_date_from,release_date_to))

            if batch_status!='all':
                audit_detail=audit_detail.filter(batch_status=batch_status)
            if db_type!='all':
                audit_detail=audit_detail.filter(db_type=db_type)
            if audit_user!='all':
                audit_detail=audit_detail.filter(audit_user=audit_user)
            if evaluator!='all':
                audit_detail=audit_detail.filter(evaluator=evaluator)
            if execute_status!='all':
                audit_detail=audit_detail.filter(execute_status=execute_status)

            re_detail=[]
            for item in audit_detail:
                tmp=item.t_ddlaudit_batch_detail_set.all().order_by('sqlnum')
                for i in tmp:
                    re_detail.append(i)
            

            if not re_detail:
                error_batch=True

        else:
            return render(request,"ddlaudit/checkresult.html",returninfo)


        if error_batch==False:
            returninfo['re_detail']=re_detail
            return render(request,"ddlaudit/checkresult.html",returninfo)
        else:
            returninfo['error_batch']=error_batch
            return render(request,"ddlaudit/checkresult.html",returninfo)


    if request.method=="GET":
        return render(request,"ddlaudit/checkresult.html",returninfo)