# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import cmdb
import datetime,time
from common import seq_generator
from ddlaudit import ddlaudit_oracle
from ddlaudit import constant
from ddlaudit import models
import chardet


@login_required(login_url="/")
def audit(request):
    if request.method=="GET":
        return render(request,'ddlaudit/audit.html')

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


    release_date = int(time.time())
    audit_user=request.user.username#审核人
    audit_batch=seq_generator.ddlaudit_batch(db_type,str(release_date),skema)

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
        result=ddlaudit_oracle.process_sqlfile(allsqltext,dict_config,onedbinfo.privilege_flag,onedbinfo.username,onedbinfo.password,\
               onedbinfo.ipadress,onedbinfo.port,onedbinfo.servicename)
    elif db_type=='mysql':
    	pass#ddlaudit_mysql.process_sqlfile(allsqltext)
    else:
    	pass

    #print result  result是一个list  {'type':'createtab','content':"sqlstr",'results':[(0,"blabla"),(1,"blabla")]}


    #批次状态
    dict_batch_status={'qualified':0,'semi-qualified':0,'unqualified':0}
    #统计DDL的数量
    sqlamount=0
    for item in result:
        if item['type'].startswith('summary_sqltype'):
            tmpstr=item['type'].replace("summary_sqltype","")
            try:
                sqlamount=int(tmpstr)
            except:
                pass
            else:
                pass

        for subitem in item['results']:
            if subitem[0]==2:
                dict_batch_status['unqualified']+=1

            elif subitem[0]==1:
                dict_batch_status['semi-qualified']+=1
                #execute_status="init"
                #continue
            else:
                dict_batch_status['qualified']+=1


    if dict_batch_status['unqualified']>0:
        batch_status='unqualified'
        execute_status="noexe"
    elif dict_batch_status['semi-qualified']>0:
        batch_status='semi-qualified'
        execute_status="init"
    else:
        batch_status="qualified"
        execute_status="init"


    # 记录到数据模型 T_DDLAUDIT_BATCH_INFO 中
    model_batch_info_insert=models.T_DDLAUDIT_BATCH_INFO(audit_user=audit_user,audit_batch=audit_batch,app_name=app_name,\
    release_date=release_date,db_type=db_type,allsqltext=allsqltext,sqlamount=sqlamount,batch_status=batch_status,execute_status=execute_status)
    model_batch_info_insert.save()




    #记录到T_DDLAUDIT_BATCH_DETAIL表中
    i=1
    for item in result:
        audit_status= 0  #"qualified"
        for subitem in item['results']:
            if subitem[0]==2:
                audit_status=2  #错误
                break
            elif subitem[0]==1:
                audit_status=1  #警告
            elif subitem[0]==3: #信息
                audit_status=3
                break
            else:
                pass


        model_batch_detail_insert=models.T_DDLAUDIT_BATCH_DETAIL(audit_batch=model_batch_info_insert,sqlnum=i,\
        sqltext=item['content'],sqltype=item['type'],audit_result=item['results'],audit_status=audit_status)
        model_batch_detail_insert.save()

        item['num']=i #给字典添加一个编号
        i=i+1




    audit_info = {
        'audit_user': audit_user,
        'audit_batch': audit_batch,
        'db_type':db_type,
        'db_name':db_name,
        'skema':skema,
        'app_name':app_name,
        'allsqltext':allsqltext,
        'result':result,
        'batch_status':batch_status,
        'sqlamount':sqlamount
    }


    # 返回到页面展示
    return render(request, 'ddlaudit/audit.html', audit_info)



