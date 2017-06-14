# -*- coding:utf-8 -*-
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from runanalysis import dbstatus_oracle
import cmdb
import inspect




@login_required(login_url="/")
def dbstatus(request):
    list_check=[
        {'type':'eventmetric',"value":"log file sync"},
        {'type':'eventmetric',"value":"log_file_parallel_write"},
        {'type':'eventmetric',"value":"enq: TX - row lock contention"},
        {'type':'eventmetric',"value":"library cache lock"},
        {'type':'eventmetric',"value":"latch: cache buffers chains"},
        {'type':'eventmetric',"value":"buffer busy waits"},
        {'type':'eventmetric',"value":"gc buffer busy acquire"},
        {'type':'eventmetric',"value":"gc buffer busy release"},
        {'type':'eventmetric',"value":"read by other session"},
        {'type':'eventmetric',"value":"db file sequential read"},
        {'type':'eventmetric',"value":"db file scattered read"},
        {'type':'eventmetric',"value":"direct path read"},

        {'type':'sysmetric',"value":"Logical Reads Per Sec"},
        {'type':'sysmetric',"value":"Physical Read Bytes Per Sec"},
        {'type':'sysmetric',"value":"Physical Write Bytes Per Sec"},
        {'type':'sysmetric',"value":"Logons Per Sec"},
        {'type':'sysmetric',"value":"Redo Generated Per Sec"},
        {'type':'sysmetric',"value":"User Commits Per Sec"},
        {'type':'sysmetric',"value":"User Transaction Per Sec"},
        {'type':'sysmetric',"value":"Database CPU Time Ratio"},
        {'type':'sysmetric',"value":"Buffer Cache Hit Ratio"},
        {'type':'sysmetric',"value":"Memory Sorts Ratio"},
        {'type':'sysmetric',"value":"User Calls Per Sec"},
        {'type':'sysmetric',"value":"Soft Parse Ratio"},

        {'type':'parameter',"value":""},

        {'type':'session',"value":""},
        {'type':'session_active',"value":""},
        {'type':'size_datafiles',"value":""},
        {'type':'size_segments',"value":""},



        {'type':'top',"value":"sql"},
        {'type':'top',"value":"session"},
        {'type':'top',"value":"event"},

        {'type':'longquery',"value":""},
        {'type':'longtrans',"value":""},


        ]
    if request.method=="GET":  
        return render(request, 'runanalysis/dbstatus.html',{'list_check':list_check})
    if request.method=="POST":  
        checkitem=request.POST.get('checkitem','')
        #print "====",checkitem
        db_name=request.POST.get('db_name','')
        db_type=request.POST.get('db_type','')
        re_queryset=cmdb.models.T_CMDB_DBINFO.objects.filter(db_type=db_type,db_name=db_name).\
        values('ipadress','port','servicename','dbausername','dbapassword').distinct()
        dict_tmp={"ipadress":re_queryset[0]['ipadress'],
                  "port":re_queryset[0]['port'],
                  "servicename":re_queryset[0]['servicename'],
                  "username":re_queryset[0]['dbausername'],
                  "password":re_queryset[0]['dbapassword']
                 }
        if db_type=="oracle":
            print "oracle"
            try:
                obj_dbstatus=dbstatus_oracle.check(**dict_tmp)
                #print getattr(obj_dbstatus,checkitem.split(".")[0])  #获取对象的方法名
                method=getattr(obj_dbstatus,checkitem.split(".")[0]) 
                argnames=inspect.getargspec(method).args[1:]   #获取方法的传入变量 列表
                if argnames!=[]:
                	list_res=method (checkitem.split(".")[1])
                else:
                	list_res=method ()
                obj_dbstatus.close()




                dict_return={"db_name":db_name,
                             "db_type":db_type,
                             "checkitem":checkitem,
                             "list_res":list_res,
                             "list_check":list_check
                            }

                return render(request, 'runanalysis/dbstatus.html',dict_return)
            except:
            	pass
            else:
                pass

        else:
            pass



 
    