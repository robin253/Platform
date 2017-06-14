# -*- coding:utf-8 -*-
from django.http import HttpResponse


from dmlaudit import models
from dmlaudit import dmlaudit_oracle
from dmlaudit import dmlaudit_mysql
from common import form_txt,sendwechat
from dmlaudit import constant
import cmdb
from common import splitor 

from django.contrib.auth.decorators import login_required


@login_required(login_url="/")
def dbause_execute(request): #ajax
    #获取前端传入的数据和后台数据库数据    
    try:
        audit_batch = request.GET['batch']
        executor=request.user.username
        re_batch_info=models.T_DMLAUDIT_BATCH_INFO.objects.get(audit_batch=audit_batch)
        re_modify=re_batch_info.t_dmlaudit_batch_detail_set.all()
        #获取连接串信息
        onedbinfo=cmdb.models.T_CMDB_DBINFO.objects.get(db_type=re_batch_info.db_type,app_name=re_batch_info.app_name)
        if onedbinfo.db_type=='oracle':
            auditobject=dmlaudit_oracle.DmlAudit(onedbinfo.username,onedbinfo.password,onedbinfo.ipadress,\
            onedbinfo.port,onedbinfo.servicename)
        elif onedbinfo.db_type=='mysql':
            auditobject=dmlaudit_mysql.DmlAudit(onedbinfo.username,onedbinfo.password,onedbinfo.ipadress,\
            onedbinfo.port,onedbinfo.skema)
            auditobject.execsql("SET autocommit=off")
    except:
        return HttpResponse("连接或后台数据异常，请刷新页面并重试")
    else:
        try:
            #防止DBA同时执行
            if re_batch_info.execute_status=='init':#必须是待执行状态
                re_batch_info.execute_status="doing"
                re_batch_info.save()
            else:
                if re_batch_info.execute_status=='suc':
                    return HttpResponse("已被他人执行成功")
                elif re_batch_info.execute_status=='fail':
                    return HttpResponse("已被他人执行失败")
                elif re_batch_info.execute_status=='doing':
                    return HttpResponse("正被他人执行中")

            #执行批次中的语句（备份）
            exefailflag=0
            backupfailflag=0
            execute_status=''
            exe_failreason=''
            #os.chdir(constant.backup_filepath)会出现报错 不要在项目中切换路径 使用绝对路径来处理
            backupflag=0
            list_backupfilename=[]

            for obj in re_modify:
                if obj.sqltype=='update'  or obj.sqltype=='delete':#需要备份
                    #获取备份语句并执行
                    func_name=obj.sqltype+"_change"
                    lexerSplitor = splitor.LexerSplitor()
                    uncomment_sqltext=lexerSplitor.remove_sqlcomment(obj.sqltext)
                    backupsql=getattr(auditobject,func_name)(uncomment_sqltext,1)#这里取消注释，备份语句一般不会出错 
                    #print backupsql
                    list_backup=auditobject.execsql(backupsql)#要么就是list 要么就是str
                    if isinstance(list_backup,str):
                        backupfailflag=1#备份语句执行失败 全流程结果
                        backupfailreason="第"+str(obj.sqlnum)+"句备份失败--"+list_backup
                        break 
                    else:
                        backupfilename=str(audit_batch)+"_"+str(obj.sqlnum)+".txt"
                        form_txt.Maketxt(constant.backup_filepath,backupfilename,list_backup) #备份到txt
                        backupflag=1
                        list_backupfilename.append(backupfilename)

                    str_failreason=auditobject.execsql(obj.sqltext) #正常是none 报错返回str （select返回list)
                    if str_failreason is not None:#isinstance(str_failreason,str)
                        exefailflag=1#语句执行失败 全流程结束
                        exefailreason="第"+str(obj.sqlnum)+"句执行失败--"+str_failreason
                        break


                else:#不需要备份
                    str_failreason=auditobject.execsql(obj.sqltext)
                    if str_failreason is not None:
                        exefailflag=1
                        exefailreason="第"+str(obj.sqlnum)+"句执行失败--"+str_failreason
                        break


            if backupflag==1:
                #压缩文件
                form_txt.Makezip(constant.backup_filepath,audit_batch+'.zip',list_backupfilename)


        except:
            if re_batch_info.execute_status=='doing':#状态还原
                re_batch_info.execute_status="init"
                re_batch_info.save()
            try:#mysql下可能是超时 会话杀掉了 close_rollback会失败的 
                auditobject.close_rollback()
            except:
                pass
            return HttpResponse("平台发生非预期错误，请刷新页面")
        else:

            if backupfailflag==1:
                execute_status = 'fail'
                exe_failreason = backupfailreason
                try: #mysql下可能是超时 会话杀掉了 close_rollback会失败的 
                    auditobject.close_rollback()
                except:
                    pass

            elif exefailflag==1:
                execute_status = 'fail'
                exe_failreason = exefailreason
                try:#mysql下可能是超时 会话杀掉了 close_rollback会失败的 
                    auditobject.close_rollback()
                except:
                    pass

            else:
                execute_status = 'suc'
                exe_failreason = ''
                auditobject.close_commit()#提交

            #存入数据库
            re_batch_info.execute_status=execute_status
            re_batch_info.exe_failreason=exe_failreason
            re_batch_info.executor=executor
            re_batch_info.save()

            #微信
            if  constant.sendwechat_flag==1:#微信开关打开时 发送微信
                try:
                    message_content=''
                    if execute_status=='fail':
                        message_content=str(audit_batch)+"批次执行失败！请线下沟通（执行人："+str(executor)+"）"
                    elif execute_status=='suc':
                        message_content=str(audit_batch)+"批次执行成功！（执行人："+str(executor)+"）"
                    if message_content!='':
                        wechat_sender = sendwechat.WeChat()#初始化对象
                        msg_dict=wechat_sender.send_messages(message_content)#调用方法发送信息 并返回信息
                except:
                    print "微信发送失败"
                else:
                    pass

            #返回执行状态 要么suc 要么fail
            if execute_status=='suc':
                return HttpResponse("成功")
            elif execute_status=='fail':
                return HttpResponse("失败")


    



    

