# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.db.models import Count #为了使用count函数做统计用
from django.db.models import Q  #w为了使用不等于函数
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


    release_date_from=year_from+month_from+day_from

    day_to=order_date_to.split('/')[0]
    month_to=order_date_to.split('/')[1]
    year_to=order_date_to.split('/')[2]

    release_date_to=year_to+month_to+day_to


    ###############################
    #统计在某一个时间段内批次情况
    re=models.T_DDLAUDIT_BATCH_INFO.objects.filter(db_type=db_type,release_date__range=(release_date_from,release_date_to))


    #batch_status批次状态  start 发起   submit 审核中   freeze 审核通过  release 已发布  cancel 已取消
    #execute_status执行状态   wait 待审核 fail 失败  suc 成功


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



    timerange=order_date_from+'-'+order_date_to



    ###############################

    
    #应用项目top 10统计图
    #SELECT app_name, COUNT(app_name) AS total  from XXX group by app_name;
    sta_exec_app_num=re.values('app_name').annotate(total=Count('app_name')).order_by('-total')[0:10] 

    #计算top 10应用的批次总数
    sta_count_app_num=0
    for aitem in sta_exec_app_num:
        sta_count_app_num=sta_count_app_num+aitem['total']
     
    #订正批次总数
    sta_exec_app_all_num=sta_all_num


    #除去top10外的其他app的订正批次数
    sta_other_ev_app_num=sta_exec_app_all_num-sta_count_app_num   

    ###############################

    #DBA执行量top 10统计图
    sta_evaluator_num=re.filter(~Q(executor= '')).values('executor').annotate(total=Count('executor')).order_by('-total')[0:10] 

    
    #计算top 10 DBA执行的批次总数
    sta_count_num=0
    for item in sta_evaluator_num:
        sta_count_num=sta_count_num+item['total']

   
    #已执行的订正批次总数
    sta_exec_all_num=re.filter(~Q(executor= '')).count()

    #除去top外的其他DBA的执行数
    sta_other_evaluator_num=sta_exec_all_num-sta_count_num

    ###############################

    #订正申请人top 10统计图
    sta_10user_info=re.values('audit_user').annotate(total=Count('audit_user')).order_by('-total')[0:10] 

    #计算top 10订正申请人总批次
    sta_10user_num=0
    for aitem in sta_10user_info:
        sta_10user_num=sta_10user_num+aitem['total']

    #订正批次总数
    sta_alluser_num=sta_all_num

    #除去top10外的其他订正申请人的订正批次数
    sta_otheruser_num=sta_alluser_num-sta_10user_num  




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

        'sta_evaluator_num':sta_evaluator_num,
        'sta_exec_all_num':sta_exec_all_num,
        'sta_other_evaluator_num':sta_other_evaluator_num,

        'sta_exec_app_num':sta_exec_app_num,
        'sta_exec_app_all_num':sta_exec_app_all_num,
        'sta_other_ev_app_num':sta_other_ev_app_num,

        'sta_10user_info':sta_10user_info,
        'sta_alluser_num':sta_alluser_num,
        'sta_otheruser_num':sta_otheruser_num,
        'return_flag':return_flag

    }
    
    #print return_info
    return render(request,"ddlaudit/report.html",return_info)