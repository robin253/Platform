# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.db.models import Count #为了使用count函数做统计用
from django.db.models import Q  #w为了使用复杂查询
from django.contrib.auth.decorators import login_required

from ddlaudit import models
import datetime

def analyseRepeat(inputlist):
    tmp_dict={}
    for item in inputlist:
        if tmp_dict.has_key(item):
            tmp_dict[item]+=1
        else:
            tmp_dict[item]=1
    return tmp_dict


@login_required(login_url="/")
def report(request):
    if request.method=="POST":
        pass

    else:
        return_info = {'return_flag':True}
        return render(request,"ddlaudit/report.html",return_info)

    db_type=request.POST['db_type']
    order_date_from=request.POST['order_date_from']
    order_date_to=request.POST['order_date_to']

    #默认查询7天
    timeformat = '%d/%m/%Y'
    #today_value=datetime.datetime.now()
    today_value=datetime.datetime.now()
    sevenbefore_value=today_value+datetime.timedelta(days=-6)
    today = today_value.strftime(timeformat)
    sevenbefore = sevenbefore_value.strftime(timeformat)
    #print today_value
    #print sevenbefore_value
    if order_date_from == '':
        order_date_from=sevenbefore
    if order_date_to == '':
        order_date_to=today
             



    day_from=order_date_from.split('/')[0]
    month_from=order_date_from.split('/')[1]
    year_from=order_date_from.split('/')[2]

    #install_data_from=year_from+'-'+month_from+'-'+day_from
    install_data_from=datetime.datetime(int(year_from),int(month_from),int(day_from),0,0,0)

    day_to=order_date_to.split('/')[0]
    month_to=order_date_to.split('/')[1]
    year_to=order_date_to.split('/')[2]

    #install_data_to=year_to+'-'+month_to+'-'+day_to
    install_data_to=datetime.datetime(int(year_to),int(month_to),int(day_to),23,59,59,999999)


    #print install_data_from
    #print install_data_to



    ###############################
    #统计在某一个时间段内批次情况
    re=models.T_DDLAUDIT_BATCH_INFO.objects.filter(db_type=db_type,created_at__range=(install_data_from,install_data_to))



    #评审不通过或取消的批次数  batch_status="unqualified" "cancel"  
    sta_noqual_num=re.filter(Q(batch_status="unqualified")|Q(batch_status="cancel")).count()


    #执行成功 execute_status='suc'
    sta_qual_suc=re.filter(batch_status="qualified",execute_status='suc').count()
    #执行失败 execute_status='fail'
    sta_qual_fail=re.filter(batch_status="qualified",execute_status='fail').count()
    #待执行 execute_status='init'  'doing'
    sta_qual_init=re.filter(batch_status="qualified").filter(Q(execute_status='init')|Q(execute_status='doing')).count()
    #评审通过的批次数  batch_status="qualified"
    sta_qual_num=sta_qual_suc+sta_qual_fail+sta_qual_init


    #评估中的批次数  batch_status="semi-qualified"
    sta_semiqual_num=re.filter(batch_status="semi-qualified").count()


    #受理的总批次数
    sta_all_num=sta_noqual_num+sta_qual_num+sta_semiqual_num

    #时间范围
    timerange=order_date_from+'-'+order_date_to





    ###############################

    
    #应用项目top 10统计图
    #SELECT app_name, COUNT(app_name) AS total  from XXX group by app_name;
    sta_10app_info=re.values('app_name').annotate(total=Count('app_name')).order_by('-total')[0:10] 

    #计算top 10应用的批次总数
    sta_10app_num=0
    for aitem in sta_10app_info:
        sta_10app_num=sta_10app_num+aitem['total']
     

    #除去top10外的其他app的订正批次数
    sta_otherapp_num=sta_all_num-sta_10app_num   



    ###############################

    #申请人top 10统计图
    sta_10user_info=re.values('audit_user').annotate(total=Count('audit_user')).order_by('-total')[0:10] 
    #print sta_10user_info

    #计算top 10订正申请人总批次
    sta_10user_num=0
    for aitem in sta_10user_info:
        sta_10user_num=sta_10user_num+aitem['total']

    #除去top10外的其他订正申请人的订正批次数
    sta_otheruser_num=sta_all_num-sta_10user_num  




    ###############################



    if re:
        return_flag=True
    else:
        return_flag=False
    return_info = {
        'db_type':db_type,
        'sta_all_num': sta_all_num,
        'sta_noqual_num': sta_noqual_num,
        'sta_qual_num': sta_qual_num,
        'sta_qual_fail': sta_qual_fail,
        'sta_qual_suc': sta_qual_suc,
        'sta_qual_init': sta_qual_init,
        'sta_semiqual_num': sta_semiqual_num,
        'timerange':timerange,



        'sta_10app_info':sta_10app_info,
        'sta_otherapp_num':sta_otherapp_num,

        'sta_10user_info':sta_10user_info,
        'sta_otheruser_num':sta_otheruser_num,

        'return_flag':return_flag

    }
    
    #print return_info
    return render(request,"ddlaudit/report.html",return_info)