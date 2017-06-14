#!/bin/env python
# -*- coding: UTF-8 -*-


from common.connect_oracle  import Oracle_Conn
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
import copy



class check():
    def __init__(self,username,password,ipadress,port,servicename):
        self.connection=Oracle_Conn(username,password,ipadress,port,servicename)

    def common_part(self,sql,tuple_colname):
        sqlres=self.connection.execsql(sql)
        if isinstance(sqlres,list):
            sqlres.insert(0,tuple_colname)
            return sqlres
        else:
            tmp_list=[]
            tmp_list.append(tuple_colname)
            return tmp_list


    def eventmetric(self,name):

        sql='''select N.name,round(E.TIME_WAITED * 10 / (CASE 
               WHEN WAIT_COUNT = 0 THEN 
               1 
               ELSE 
               WAIT_COUNT 
               END), 
               2) WAIT_MS 
              FROM V$EVENTMETRIC E ,V$EVENT_NAME N  WHERE E.EVENT_ID = N.EVENT_ID
              and N.NAME= '{0}' '''.format(name)
        return self.common_part(sql,("EVENTMETRIC_NAME","WAIT_MS"))


    
    def sysmetric(self,name):
        sql = '''select METRIC_NAME,round(value,2) from v$sysmetric 
              where METRIC_NAME ='{0}' and 
              rownum <=1 order by INTSIZE_CSEC desc'''.format(name)
        return self.common_part(sql,("SYSMETRIC_NAME","VALUE")) 


    def session(self):
        sql ='''select count(*) from v$session where  type!='BACKGROUND' '''
        return self.common_part(sql,("SESSCOUNT",))



    def session_active(self):
        sql ='''select count(*) from v$session where  type!='BACKGROUND' and status='ACTIVE' '''
        return self.common_part(sql,("ACTIVE_SESSCOUNT",))

    def size_datafiles(self):
        sql = '''select round(sum(bytes/1024/1024/1024),2)
              from dba_data_files'''
        return self.common_part(sql,("DATAFILE_SIZE_G",))



    def size_segments(self):
        sql =   '''select round(sum(bytes/1024/1024/1024),2)
              from dba_segments '''
        return self.common_part(sql,("SEGMENT_SIZE_G",))

    def top(self,name):
        minute="5"
        if name=="sql":
            sql='''
            select * from 
            (select  SQL_ID , SQL_PLAN_HASH_VALUE plan_hash_value, sql_opname, 
            sum(decode(session_state,'ON CPU',1,0))     "CPU", 
            sum(decode(session_state,'WAITING',1,0))    - 
            sum(decode(session_state,'WAITING', decode(wait_class, 'User I/O',1,0),0))    "OTHER_WAIT" , 
            sum(decode(session_state,'WAITING', decode(wait_class, 'User I/O',1,0),0))    "IO_WAIT" , 
            sum(decode(session_state,'ON CPU',1,1))     "TOTAL" 
            from v$active_session_history where SQL_ID is not NULL 
            and sample_time > sysdate - {0}/24/60
            group by sql_id, SQL_PLAN_HASH_VALUE   , sql_opname
            order by sum(decode(session_state,'ON CPU',1,1))   desc ) 
            where  rownum < 10'''.format(minute)
            return self.common_part(sql,("SQL_ID","PLAN_HASH_VALUE","SQL_OPNAME","CPU","OTHER_WAIT","IO_WAIT","TOTAL"))

        elif name=="session":
            sql='''
             select * from 
                   (select ash.session_id,
                           ash.session_serial#,
                           ash.machine,
                           ash.sql_id,
                           b.USERNAME,
                           sum(decode(ash.session_state,'ON CPU',1,0))     "CPU_WAIT", 
                           sum(decode(ash.session_state,'WAITING', decode(ash.wait_class, 'User I/O',1,0),0))    "IO_WAIT" ,
                           sum(decode(ash.session_state,'WAITING',1,0))    - 
                           sum(decode(ash.session_state,'WAITING', decode(ash.wait_class, 'User I/O',1,0),0))    "OTHER_WAIT" ,    
                           sum(decode(ash.session_state,'ON CPU',1,1))     "TOTAL" 
                      from V$ACTIVE_SESSION_HISTORY ash,dba_users b
                     where sample_time >sysdate -{0}/24/60
                     and ash.user_id=b.user_id
                     group by ash.session_id,ash.session_serial#,ash.machine,ash.sql_id,b.username
            order by sum(decode(ash.session_state,'ON CPU',1,1))   desc) where rownum<10 '''.format(minute)
            return self.common_part(sql, 
                 ( "SESSION_ID",
                   "SERIAL#",
                   "MACHINE",
                   "SQL_ID",
                   "USERNAME",
                   "CPU",
                   "IO",
                   "OTHER",
                   "TOTAL"))

        elif name=="event":
            pass

        else:
            pass
        

    
    def longquery(self):
        pass

    def longtrans(self):
        pass


    #redo

    #temp tablespace

    #tablespace 

    #instance info  uptime

    #undo

    #lock

    #DG

    #wait event

    #pga sga

    def parameter(self):
        sql='''
        select name,value,ISSES_MODIFIABLE,ISSYS_MODIFIABLE from  v$parameter where  name in 
        ('db_name','db_files','db_writer_processes','db_block_size','db_file_multiblock_read_count',
        'processes','sessions','open_cursors','session_cached_cursors','undo_management',
        'undo_retention','job_queue_processes','fast_start_mttr_target','log_checkpoints_to_alert',
        'log_checkpoint_timeout','log_checkpoint_interval','statistics_level','timed_statistics',
        'log_archive_max_processes','control_file_record_keep_time','cursor_sharing',
        'deferred_segment_creation','optimizer_features_enable','optimizer_mode',
        'parallel_max_servers','remote_login_passwordfile','archive_lag_target',
        'audit_trail','filesystemio_options','disk_asynch_io','memory_max_target',
        'memory_target','workarea_size_policy','pga_aggregate_target','sga_max_size',
        'sga_target','lock_sga','db_cache_size','db_cache_advice','shared_pool_size',
        'large_pool_size','java_pool_size','streams_pool_size','log_buffer',
        'db_block_checking','db_block_checksum','db_lost_write_protect','db_ultra_safe')'''
        sqlres=self.connection.execsql(sql)
        if isinstance(sqlres,list):
            sqlres.insert(0,("PARAMETER_NAME","VALUE","ISSES_MODIFIABLE","ISSYS_MODIFIABLE",))
            return sqlres
        else:
            return [("PARAMETER_NAME","VALUE","ISSES_MODIFIABLE","ISSYS_MODIFIABLE",),(sqlres,"","","",)]


    def close(self):
        self.connection.close_commit()