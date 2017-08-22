# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

import cmdb
from ddlaudit.check_online_structure import CheckOnlineStructure
from ddlaudit.list_manipulation import delRepeat

@login_required(login_url="/")
def structure(request):

    if request.method=="GET":
        return render(request,'ddlaudit/structure.html')
    
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
            return render(request,'ddlaudit/structure.html', audit_info)
        else:
            pass

 
       
        #如果输入框文本为空
        if not allsqltext:
            audit_info = {
            'errmsg':"审核文本为空",
            'db_type':db_type,
            'db_name':db_name,
            'skema':skema,
            'app_name':app_name
                        }
            return render(request,'ddlaudit/structure.html', audit_info)
        

    #开始审核
    if db_type=='oracle':
        #查询线上结构和表 
        checkobj=CheckOnlineStructure(onedbinfo.username,onedbinfo.password,onedbinfo.ipadress,onedbinfo.port,onedbinfo.servicename)
        
        allsqltext=allsqltext.replace("，",",")
        list_table=allsqltext.split(",")
        list_real_table=[]
        for tablename in list_table:
            print tablename
            res=checkobj.check_tab(tablename)
            if res:
                for item in res:
                    list_real_table.append(item[0])
        list_real_table=delRepeat(list_real_table)
        
        list_tab=[]
        list_col=[]
        list_ind=[]
        list_tab_part=[]
        list_ind_part=[]
        for item in list_real_table:
            res_tab,res_col,res_ind,res_tab_part,res_ind_part=checkobj.get_info(item)
            for item in res_tab:
                list_tab.append(item)
            for item in res_col:  
                list_col.append(item)
            for item in res_ind: 
                list_ind.append(item)
            for item in res_tab_part: 
                list_tab_part.append(item)
            for item in res_ind_part: 
                list_ind_part.append(item)

        checkobj.close()
        

    elif db_type=='mysql':
    	pass
    else:
    	pass

    #print list_tab,list_col,list_ind,list_tab_part,list_ind_part
    
    audit_info = {
            'db_type':db_type,
            'db_name':db_name,
            'skema':skema,
            'app_name':app_name,
            'allsqltext':allsqltext,
            'list_tab':list_tab,
            'list_col':list_col,
            'list_ind':list_ind,
            'list_tab_part':list_tab_part,
            'list_ind_part':list_ind_part
                         }

    #返回到页面展示
    return render(request,'ddlaudit/structure.html', audit_info)
   
        
