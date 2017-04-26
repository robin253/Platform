# -*- coding:utf-8 -*-
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from runanalysis import reportmaker_oracle
from runanalysis import constant
import datetime
import os
import cmdb 


   
#AWR Automatic Workload Repository
@login_required(login_url="/")
def statreport_awr(request):

    def getpageinfo():
        list_hour=range(24)
        re_queryset=cmdb.models.T_CMDB_DBINFO.objects.values('db_name').distinct()
        list_db_name=[]
        for item in re_queryset:
            list_db_name.append(item['db_name'])

        dict_file={}
        reportfile_path=constant.reportfile_path
        for item in os.listdir(reportfile_path):#获取当前路径下的目录名和文件名
            if item.startswith("awrrpt") and item.endswith(".html"):
                dict_file[item]=os.path.getmtime(os.path.join(reportfile_path,item))#获取文件更新时间
        #print dict_file.items() #输出列表 里面是元祖
        list_file = sorted(dict_file.items(), key=lambda e:e[1], reverse=True)#按时间大小排序
        list_showfile=[]
        for i in range(len(list_file)):
            if i==10:
                break #最多10条
            else:
                list_showfile.append(list_file[i][0])
        list_showfile=tuple(list_showfile)

        dict_re={'list_hour':list_hour,
                 'list_db_name':list_db_name,
                 'list_showfile':list_showfile}
        return dict_re


    if request.method=="GET":  
        return render(request, 'runanalysis/statreport_awr.html',getpageinfo())

    if request.method=="POST":  
        db_name=request.POST['db_name']
        date=request.POST['date']
        beginhr=request.POST['beginhr']
        endhr=request.POST['endhr']
        instance_number=request.POST['instance_number']

        if date=='':
            today_value=datetime.datetime.now()
            date=today_value.strftime('%Y%m%d')#默认当天
        else:
            day=date.split('/')[0]
            month=date.split('/')[1]
            year=date.split('/')[2]
            date=year+month+day

        if len(beginhr)==1:
            beginhr='0'+beginhr
        if len(endhr)==1:
            endhr=  '0'+endhr

        re_queryset=cmdb.models.T_CMDB_DBINFO.objects.filter(db_name=db_name).\
        values('ipadress','port','servicename','dbausername','dbapassword').distinct()

        dict_tmp={"ipadress":re_queryset[0]['ipadress'],
                  "port":re_queryset[0]['port'],
                  "servicename":re_queryset[0]['servicename'],
                  "dbausername":re_queryset[0]['dbausername'],
                  "dbapassword":re_queryset[0]['dbapassword'],
                  "date":date,
                  "beginhr":beginhr,
                  "endhr":endhr,
                  "instance_number":instance_number
                  }
        #print dict_tmp

        returninfo=reportmaker_oracle.getawr(**dict_tmp)

        if returninfo.startswith('Success'):
            errflag=False
        else:
            errflag=True

        dict_pageinfo=getpageinfo()
        dict_pageinfo['returninfo']=returninfo
        dict_pageinfo['errflag']=errflag
        
        return render(request, 'runanalysis/statreport_awr.html',dict_pageinfo)