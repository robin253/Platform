#!/bin/env python
# -*- coding: UTF-8 -*-

from common.connect_oracle  import Oracle_Conn
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'#防止oracle中文返回出现乱码
from sqlstat_config import planchange_dict,planchange_checksql,inefficient_dict,inefficient_checksql


#获取执行计划改变的SQL
def planchange(ipadress,port,servicename,dbausername,dbapassword,parsing_shema_name):
    try:
        connection = Oracle_Conn(dbausername, dbapassword, ipadress, port, servicename)
    except:
        return "Error:数据库无法连接"
    else:
        pass

    tmpsql=planchange_checksql.format(parsing_shema_name,\
    planchange_dict['CHANGE_RATE'],\
    planchange_dict['EXECUTIONS'],\
    planchange_dict['AVG_TIME_MS'])
    print tmpsql
  
    re_planchange=connection.execsql(tmpsql) #要么报错str要么就是list

    if isinstance(re_planchange,str):
        connection.close_commit()
        return "Error:获取信息异常"
    else:
        connection.close_commit()
        #print re_planchange
        list_planchange=[]
        for item in re_planchange:
    	    dict_tmp={'inst_id':item[0],
    		          'sql_id':item[1],
    		          'sql_text':item[2],
    		          'plan_hash_value':item[3],
    		          'first_load_time':item[4],
    		          'last_active_time':item[5],
    		          'max_last_active_time':item[6],
    		          'executions':item[7],
    		          'avg_time_ms':item[8],
    		          'best_avg_time_ms':item[9],
    		          'change_rate':item[10]
    		          }
            list_planchange.append(dict_tmp)
        return list_planchange






#获取低效sql
def inefficient(ipadress,port,servicename,dbausername,dbapassword,parsing_shema_name):
    try:
        connection = Oracle_Conn(dbausername, dbapassword, ipadress, port, servicename)
    except:
        return "Error:数据库无法连接"
    else:
        pass

    tmpsql=inefficient_checksql.format(parsing_shema_name,\
    inefficient_dict['EXECUTIONS'],inefficient_dict['EXE_MIN_SINCE'],\
    inefficient_dict['AVG_TIME_MS'],inefficient_dict['AVG_GETS_MB'],inefficient_dict['AVG_READS_MB'])
  
    re_inefficient=connection.execsql(tmpsql) #要么报错str要么就是list
    #print re_inefficient

    if isinstance(re_inefficient,str):
        connection.close_commit()
        return "Error:获取信息异常"
    else:
        list_inefficient=[]
        for item in re_inefficient:
            #print type(item[2])  clob
            dict_tmp={'inst_id':item[0],
                      'sql_id':item[1],
                      'sql_text':item[2].read(), #转为str 注意read()在close_commit之前
                      'plan_hash_value':item[3],
                      'first_load_time':item[4],
                      'last_active_time':item[5],
                      'executions':item[6],
                      'avg_time_ms':item[7],
                      'avg_gets_mb':item[8],
                      'avg_reads_mb':item[9]
                      }
            list_inefficient.append(dict_tmp)
        connection.close_commit()
        return list_inefficient




