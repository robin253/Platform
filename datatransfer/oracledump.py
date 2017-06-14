#!/bin/env python
# -*- coding: UTF-8 -*-


import sys
from common.connect_oracle import Oracle_Conn
import os
import datetime
import paramiko
import md5
import logging


logger = logging.getLogger(__name__)

#md5加密函数
def md5_digest(s):
    return md5.md5(s).hexdigest()

class  expdp_process():
    def __init__(self,dbausername,dbapassword,ipadress,port,servicename,directory,\
                  tables,parallel,content,additional,skema,sysuser,syspassword):
        self.connection=Oracle_Conn(dbausername,dbapassword,ipadress,port,servicename)
        self.ipadress=ipadress
        self.port=port
        self.servicename=servicename
        self.directory=directory
        self.tables=tables
        self.parallel=parallel
        self.content=content
        self.additional=additional
        self.skema=skema
        self.sysuser=sysuser
        self.syspassword=syspassword

    def get_dumpfilepath(self):
        try:
            repath=self.connection.execsql("select directory_path from dba_directories where directory_name='{0}'".format(self.directory)) 
        except:
            return "error"
        else:
            pass

        if isinstance(repath,str):
            return "error"
        else:
            if repath==[]:
                return "error"
            else:
                pathname=repath[0][0]
                if pathname.endswith('/'):
                    return pathname[0:-1]
                else:
                    return pathname


    def get_expdpcommand(self):
        today_value=datetime.datetime.now()
        date=today_value.strftime('%Y%m%d%H%M')
        jobname=self.skema+date
        expdpcommand='''expdp "'/ as sysdba'" directory={0} dumpfile={1}.dmp logfile={2}.log tables={3} cluster=N compression=all  reuse_dumpfiles=y job_name={4} parallel={5} content={6} {7}'''\
        .format(self.directory,jobname+"%U",jobname,self.tables,jobname,self.parallel,self.content,self.additional)

        return  jobname,expdpcommand
    
    #预估数据量
    def get_segments_bytes(self):
        list_tmp=[]
        list_tables=self.tables.split(',') #owner.t1,owner.t2
        for item in list_tables:
            list_tmp.append(item.split('.')[1])
        str_tablename="','".join(list_tmp)
        str_tablename="'"+str_tablename+"'"
        #print str_tablename

        try:
            reseg=self.connection.execsql("select sum(bytes/1024/1024) from dba_segments where owner='{0}' and segment_name in ({1})".format(self.skema,str_tablename))
        except:
            return "error"
        else:
            if isinstance(reseg,str):
                return "error"
            if reseg==[]:
                return "error"
            else:
                return reseg[0][0]

    #检查表是否存在
    def check_tables(self):
        list_tmp=[]
        list_tables=self.tables.split(',') #owner.t1,owner.t2
        for item in list_tables:
            list_tmp.append(item.split('.')[1])
        str_tablename="','".join(list_tmp)
        str_tablename="'"+str_tablename+"'"
        #print str_tablename
        try:
            retables=self.connection.execsql("select table_name from dba_tables where owner='{0}' and table_name in ({1})".format(self.skema,str_tablename))
        except:
            return "error"
        else:
            if isinstance(retables,str):
                return "error"
            list_tabnames=[]
            for item in retables:
                list_tabnames.append(item[0])
            #返回差集    
            list_return=list(set(list_tmp).difference(set(list_tabnames)))
            return  ','.join(list_return)



    #表空间查询
    def get_tablespace(self):

        list_tmp=[]
        list_tables=self.tables.split(',') #owner.t1,owner.t2
        for item in list_tables:
            list_tmp.append(item.split('.')[1])
        str_tablename="','".join(list_tmp)
        str_tablename="'"+str_tablename+"'"
        #print str_tablename
        tablespace_sql='''
           select distinct tablespace_name
           from dba_segments
           where owner = '{0}'
           and segment_name in ({1})'''.format(self.skema.upper(),str_tablename)
        tablespace_idx_sql='''
           select distinct tablespace_name
           from dba_segments
           where (owner, segment_name) in
               (select owner, index_name
                  from dba_indexes
                 where owner='{0}'
                 and table_name in ({1})
               ) '''.format(self.skema.upper(),str_tablename)
        dict_return={}
        try:
            retablespace=self.connection.execsql(tablespace_sql)
        except:
            dict_return['tab']=""
        else:
            list_tmp=[]
            for item in retablespace:
                list_tmp.append(item[0])
            dict_return['tab']=','.join(list_tmp)

        try:
            retablespace_idx=self.connection.execsql(tablespace_idx_sql)
        except:
            dict_return['idx']=""
        else:
            list_tmp=[]
            for item in retablespace_idx:
                list_tmp.append(item[0])
            dict_return['idx']=','.join(list_tmp)
        return dict_return

    
    def close(self):
        self.connection.close_commit()

    def get_oracle_env(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ipadress,22,self.sysuser, self.syspassword) 
            stdin, stdout, stderr = ssh.exec_command("cat .bash_profile|grep ORACLE_" )
            oracle_env=stdout.read()#返回内容是stdout
        except:
            return ""
        else:
            ssh.close()
            return oracle_env


    def start_expdp(self,jobname,expdpcommand):


        pathname=self.get_dumpfilepath()
        #if pathname=="Error":
        #    logger.info("导出任务job_name:%s发起失败，导出路径获取异常",jobname)
        #    return 'fail',"导出任务job_name:%s发起失败，导出路径获取异常"%jobname

    
        oracle_env=self.get_oracle_env()
        if oracle_env=="":
            logger.info("导出任务job_name:%s发起失败，环境变量获取异常",jobname)
            return 'fail',"导出任务job_name:%s发起失败，环境变量获取异常"%jobname
        
        logger.info("准备发起导出任务job_name:%s",jobname)
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ipadress,22,self.sysuser, self.syspassword) 
            logger.info(" 发起导出任务job_name:%s (%s:%s/%s)\n 导出命令%s", jobname,self.ipadress,self.port,self.servicename,expdpcommand)
            stdin, stdout, stderr = ssh.exec_command(oracle_env+'\n'+expdpcommand )
            list_logfile=stderr.readlines()#日志是stderr中输出的
            logger.info(" 导出任务job_name:%s结束", jobname)
            stdin, stdout, stderr = ssh.exec_command('cd '+ pathname+ ' \n'+ 'ls |grep '+jobname+'*dmp|wc -l')
            numdumpfile=stdout.read() #返回内容是stdout
        except:
            logger.info(" 导出任务job_name:%s执行异常", jobname)
            return "fail","导出任务job_name:%s执行异常"%jobname
        else:
            ssh.close()
            logger.info(" 导出任务job_name:%s日志：%s", jobname,''.join(list_logfile))




            for i in list_logfile:
                if i.startswith('''Job "SYS"."'''+jobname): 
                    if i.find("successfully completed")!=-1:
                        status="suc"
                    else:
                        status='warning'


            #if numdumpfile!=self.parallel:
            #    status='warning'

            return status,''.join(list_logfile)


class  impdp_process(expdp_process):
    def __init__(self,dbausername,dbapassword,ipadress,port,servicename,directory,skema,sysuser,syspassword,\
                  table_exists_action,remap_table,expdp_job_name,expdp_skema,tables,\
                  expdp_tablespace,expdp_dumpfilepath,expdp_parallel):
        self.connection=Oracle_Conn(dbausername,dbapassword,ipadress,port,servicename)
        self.ipadress=ipadress
        self.port=port
        self.servicename=servicename
        self.directory=directory
        self.skema=skema
        self.sysuser=sysuser
        self.syspassword=syspassword
        self.table_exists_action=table_exists_action
        self.remap_table=remap_table
        self.expdp_job_name=expdp_job_name
        self.expdp_skema=expdp_skema
        self.tables=tables
        self.expdp_tablespace=expdp_tablespace
        self.expdp_dumpfilepath=expdp_dumpfilepath
        self.expdp_parallel=expdp_parallel



    #def get_dumpfilepath(self):继承

    #def check_tables(self):继承

    #def close(self):继承

    #def get_oracle_env(self):继承

    def get_tablespace(self):

        tablespace_sql='''select tablespace_name from  DBA_TS_QUOTAS where username='{0}' '''.format(self.skema.upper())
        #tablespace_sql2='''select distinct tablespace_name from dba_segments where owner='{0}' '''.format(self.skema.upper())
        dict_return={}.fromkeys(['idx','tab'])
        try:
            retablespace=self.connection.execsql(tablespace_sql)
        except:
            return dict_return
        else:
            if isinstance(retablespace,str):
                return dict_return
            if retablespace==[]:
                return dict_return
            else:
                for item in retablespace:
                    if item[0].endswith("IDX"):
                        dict_return['idx']=item[0]
                    if item[0].endswith("DATA"):
                        dict_return['tab']=item[0]
                return dict_return


    def get_impdpcommand(self):
        impdp_job_name="IMP_"+self.expdp_job_name

        dict_tablespace=self.get_tablespace()
        dict_expdp_tablespace=eval(self.expdp_tablespace)
        tmp_list=[]
        if dict_tablespace['tab']:
            for item in dict_expdp_tablespace['tab'].split(","):
                tmp_list.append(item+":"+dict_tablespace['tab'])
        if dict_tablespace['idx']:
            for item in dict_expdp_tablespace['idx'].split(","):
                tmp_list.append(item+":"+dict_tablespace['idx'])
        

        remap_tablespace=""
        remap_table=""
        remap_schema=""
        if tmp_list!=[]:
            remap_tablespace="remap_tablespace="+','.join(tmp_list)
        if self.remap_table!="":
            remap_table="remap_table="+self.remap_table
        if self.expdp_skema!=self.skema:
            remap_schema="remap_schema="+self.expdp_skema+":"+self.skema

        remap_info=""
        if remap_table:
            remap_info=remap_info+remap_table+" "
        if remap_schema:
            remap_info=remap_info+remap_schema+" "
        if remap_tablespace:
            remap_info=remap_info+remap_tablespace+" "



        impdpcommand='''impdp "'/ as sysdba'" directory={0} dumpfile={1}.dmp logfile={2}.log tables={3} cluster=N job_name={4} parallel={5} table_exists_action={6} {7}'''\
        .format(self.directory,self.expdp_job_name+"%U",impdp_job_name,self.tables,impdp_job_name,self.expdp_parallel,self.table_exists_action,remap_info)

        return  impdp_job_name,impdpcommand


    def start_impdp(self,impdp_job_name,impdpcommand):
        #impdp_job_name,impdpcommand=self.get_impdpcommand()
        pathname=self.get_dumpfilepath()
        oracle_env=self.get_oracle_env()
        if oracle_env=="":
            logger.info("导入任务job_name:%s发起失败，环境变量获取异常",impdp_job_name)
            return 'fail',"导入任务job_name:%s发起失败，环境变量获取异常"%impdp_job_name
        logger.info("准备发起导入任务job_name:%s",impdp_job_name)
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ipadress,22,self.sysuser, self.syspassword) 
            logger.info(" 发起导入任务job_name:%s (%s:%s/%s)\n 导入命令%s", impdp_job_name,self.ipadress,self.port,self.servicename,impdpcommand)
            stdin, stdout, stderr = ssh.exec_command(oracle_env+'\n'+impdpcommand)
            list_logfile=stderr.readlines()#日志是stderr中输出的
            logger.info(" 导入任务job_name:%s结束", impdp_job_name)
        except:
            logger.info(" 导入任务job_name:%s执行异常", impdp_job_name)
            return "fail","导入任务job_name:%s执行异常"%impdp_job_name
        else:
            ssh.close()
            logger.info(" 导入任务job_name:%s日志：%s", impdp_job_name,''.join(list_logfile))


            for i in list_logfile:
                if i.startswith('''Job "SYS"."'''+impdp_job_name): 
                    if i.find("successfully completed")!=-1:
                        status="suc"
                    else:
                        status='warning'

            return status,''.join(list_logfile)



    def trans_dmpfile(self,exp_dumpname,exp_path,imp_path):
        try:
            #下载导出文件到本地
            t = paramiko.Transport((self.source_ip,22))
            t.connect(username = self.source_sysuser, password = self.source_syspassword)
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp.get(exp_path+"/"+exp_dumpname,self.local_path+"/"+exp_dumpname)
            t.close()
            #从本地上传导出文件到目标库
            t2= paramiko.Transport((self.target_ip,22))
            t2.connect(username = self.target_sysuser, password = self.target_syspassword)
            sftp2 = paramiko.SFTPClient.from_transport(t2)
            sftp2.put(self.local_path+"/"+exp_dumpname,imp_path+"/"+exp_dumpname)
            t2.close()
        except:
            log(self.local_logfile,'dumpfile transfer fail')
            return "F"
        else:
            log(self.local_logfile,'dumpfile has been successly transfered\n[source] '+\
            self.source_ip+":"+exp_path+"/"+exp_dumpname+"\n[target] "+self.target_ip+":"+imp_path+"/"+exp_dumpname)
            return "S"



  



