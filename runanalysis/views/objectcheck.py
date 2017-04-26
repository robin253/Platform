# -*- coding:utf-8 -*-
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

import cmdb
from runanalysis import objectcheck_oracle
from runanalysis import constant
import os
import chardet
import datetime
from common import form_xlsx

@login_required(login_url="/")
def objectcheck(request):
    if request.method=="GET":  
        return render(request, 'runanalysis/objectcheck.html')

    if request.method=="POST":  
        #查询报告
        if request.POST.has_key('check'):
            db_type=request.POST.get('db_type_check','')
            db_name=request.POST.get('db_name_check','')
            skema=request.POST.get('skema_check','')
            re_queryset=cmdb.models.T_CMDB_DBINFO.objects.filter(db_type=db_type,db_name=db_name,skema=skema).\
                  values('ipadress','port','servicename','username','password').distinct()
            if re_queryset:
                prefix=skema
            else:
                return render(request, 'runanalysis/objectcheck.html',{'checkerrflag':True,'checkreturninfo':"找不到相应skema"})



            list_file=[]
            reportfile_path=constant.reportfile_path
            for item in os.listdir(reportfile_path):#获取当前路径下的目录名和文件名
                #print type(item)#str 是ascii码
                item2=item.decode(chardet.detect(item)['encoding'])
                #print item2
                if item2.startswith(prefix) and item2.endswith('xlsx'):
                    list_file.append(item2)

            list_file.reverse()
            if list_file:
                list_showfile=tuple(list_file[0:5])
                return render(request, 'runanalysis/objectcheck.html',{'checkreturninfo':list_showfile})
            else:
                return render(request, 'runanalysis/objectcheck.html',{'checkerrflag':True,'checkreturninfo':"此schema从未生成过报告"})

        else:
            pass        


        #生成报告
        db_type=request.POST.get('db_type','')
        db_name=request.POST.get('db_name','')
        skema=request.POST.get('skema','')
        #print db_type,db_name,skema
        re_queryset=cmdb.models.T_CMDB_DBINFO.objects.filter(db_type=db_type,db_name=db_name,skema=skema).\
                  values('ipadress','port','servicename','username','password','default_data_tbs','default_ind_tbs').distinct()
        if re_queryset:
            dict_tmp={"ipadress":re_queryset[0]['ipadress'],
                      "port":re_queryset[0]['port'],
                      "servicename":re_queryset[0]['servicename'],
                      "username":re_queryset[0]['username'],
                      "password":re_queryset[0]['password']
                      }
            dict_config=constant.dict_config

            data_tbs=re_queryset[0]['default_data_tbs']
            ind_tbs =re_queryset[0]['default_ind_tbs']
            if data_tbs:
                dict_config['data_tbs']=data_tbs
            if ind_tbs:
                dict_config['ind_tbs']=ind_tbs 
            dict_tmp['dict_config']=dict_config

            list_elementcheck=[]
            tables=request.POST.get('tables','')
            tablespacecheck=request.POST.get('tablespacecheck','')
            standardcolcheck=request.POST.get('standardcolcheck','')
            indexes=request.POST.get('indexes','')
            comments=request.POST.get('comments','')
            sequences=request.POST.get('sequences','')
            if tables=='tables':
                list_elementcheck.append('tables')
            if indexes=='indexes':
                list_elementcheck.append('indexes')
            if comments=='comments':
                list_elementcheck.append('comments')
            if sequences=='sequences':
                list_elementcheck.append('sequences')
            #print list_elementcheck


            if db_type=="oracle":
                try:
                    checkinstance=objectcheck_oracle.check(**dict_tmp)
                except:
                    return render(request, 'runanalysis/objectcheck.html',{'errflag':True,'returninfo':"数据库无法连接"})
                else:
                    pass
                list_returninfo=checkinstance.check_elements(list_elementcheck,tablespacecheck,standardcolcheck)#获取相关信息了
                #print list_returninfo
                
                
                list_xlsxinfo=[]
                for i in list_returninfo:
                    list_xlsxinfo.append((i['object'],i['object_type'],i['problem']))
                #print list_xlsxinfo

                #记录到xlsx文件
                reportfile_path=constant.reportfile_path
                timeformat = '%Y%m%d'
                today_value=datetime.datetime.now()
                today = today_value.strftime(timeformat)
                filename=skema+"_" +today+".xlsx"
                #print filename
                makefile=form_xlsx.Makexlsx(reportfile_path,filename)
                makefile.add_worksheet('OBJECTCHECK')
                makefile.insert_worksheet_title(['object','object_type','problem'])
                makefile.insert_worksheet_row(list_xlsxinfo)
                makefile.close_workbook()



                return render(request, 'runanalysis/objectcheck.html',{'list_returninfo':list_returninfo,'filename':filename})



            if db_type=="mysql":
                pass#前端暂时不会传入 这个逻辑不会走到 预留

 
        else:
            return render(request, 'runanalysis/objectcheck.html',{'errflag':True,'returninfo':"找不到相应skema"})

