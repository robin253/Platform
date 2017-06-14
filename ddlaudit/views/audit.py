# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import cmdb
import datetime
from common import seq_generator
from ddlaudit import ddlaudit_oracle
from ddlaudit import constant
from ddlaudit import models

@login_required(login_url="/")
def audit(request):
    if request.method=="GET":
        return render(request,'ddlaudit/audit.html')
    
    if request.method=="POST":
        db_type=request.POST.get('db_type','')
        db_name=request.POST.get('db_name','')
        skema=request.POST.get('skema','')
        app_name=request.POST.get('app_name','')
        date=request.POST.get('date','')
        allsqltext=request.POST.get('allsqltext','')#print type(allsqltext) #unicode
        try:
            onedbinfo=cmdb.models.T_CMDB_DBINFO.objects.get(db_type=db_type,db_name=db_name,skema=skema,app_name=app_name)
        except:#如果结果是多个对象 或者无返回结果，会抛出异常
            audit_info={'errmsg':"无对应数据库信息"}
            return render(request,'ddlaudit/audit.html', audit_info)
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
                return render(request,'ddlaudit/audit.html', audit_info)
        
        #如果输入框文本为空
        if not allsqltext:
            audit_info = {
            'errmsg':"审核文本为空",
            'db_type':db_type,
            'db_name':db_name,
            'skema':skema,
            'app_name':app_name
                        }
            return render(request,'ddlaudit/audit.html', audit_info)

    if date=='':
        today_value=datetime.datetime.now()
        twoafter_value=today_value+datetime.timedelta(days=+2)
        twoafter=twoafter_value.strftime('%d/%m/%Y')
        release_date=twoafter
    else:
    	release_date=date
    day=release_date.split('/')[0]
    month=release_date.split('/')[1]
    year=release_date.split('/')[2]
    release_date=year+month+day
    print release_date



    audit_user=request.user.username#审核人
    audit_batch=seq_generator.ddlaudit_batch(db_type,release_date,skema)

    #配置文件
    dict_config=constant.dict_config
    re_queryset=cmdb.models.T_CMDB_DBINFO.objects.filter(db_type=db_type,db_name=db_name,skema=skema,app_name=app_name).\
    values('default_data_tbs','default_ind_tbs').distinct()
    if re_queryset:
        data_tbs=re_queryset[0]['default_data_tbs']
        ind_tbs =re_queryset[0]['default_ind_tbs']
        if data_tbs:
            dict_config['data_tbs']=data_tbs
        if ind_tbs:
            dict_config['ind_tbs']=ind_tbs 

    #开始审核
    if db_type=='oracle':
        result=ddlaudit_oracle.process_sqlfile(allsqltext,dict_config)  
    elif db_type=='mysql':
    	pass#ddlaudit_mysql.process_sqlfile(allsqltext)
    else:
    	pass
    
    #print result  result是一个list  {'status':,'type':'','content':"",'results':[xx,blabla]}


    sqlamount=0
    for item in result:
        if item['type']=="N/A":
            pass
        else:
            sqlamount=sqlamount+1
            
    # 记录到数据模型 T_DDLAUDIT_BATCH_INFO 中    
    model_batch_info_insert=models.T_DDLAUDIT_BATCH_INFO(audit_user=audit_user,audit_batch=audit_batch,app_name=app_name,\
    db_type=db_type,allsqltext=allsqltext,sqlamount=sqlamount,batch_status='start',execute_status='wait',\
    release_date=release_date)
    model_batch_info_insert.save()

    i=1
    summary=[]
    summary_status=0
    for item in result: #{'status':,'type':'','content':"",'results':[xx,blabla]}
        if item['type']=="N/A":
            strtmp="==="+item['content']+"===\n"+'\n'.join(item['results'])
            summary.append(strtmp)
            if item['status']==1:
                summary_status=1
        else:
            #记录到数据模型 T_DDLAUDIT_BATCH_DETAIL 中
            model_batch_detail_insert=models.T_DDLAUDIT_BATCH_DETAIL(audit_batch=model_batch_info_insert,sqlnum=i,\
            sqltext=item['content'],sqltype=item['type'],audit_result=item['results'],audit_status=item['status'])
            model_batch_detail_insert.save()
        i=i+1     
    model_batch_detail_insertsummary=models.T_DDLAUDIT_BATCH_DETAIL(audit_batch=model_batch_info_insert,sqlnum=0,\
    sqltext='summary',sqltype='N/A',audit_result=summary,audit_status=summary_status)
    model_batch_detail_insertsummary.save()

 
    audit_info = {
        'audit_user': audit_user,
        'audit_batch': audit_batch,
        'db_type':db_type,
        'db_name':db_name,
        'skema':skema,
        'app_name':app_name,
        'allsqltext':allsqltext,
        'result':result
    }


    # 返回到页面展示
    return render(request, 'ddlaudit/audit.html', audit_info)



