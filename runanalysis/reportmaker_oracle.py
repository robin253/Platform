#!/bin/env python
# -*- coding: UTF-8 -*-

from common.connect_oracle  import Oracle_Conn
import constant
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'#防止oracle中文返回出现乱码


#将数据库查询结果写入html文件
def makehtml(filename,list_input):
    reportfile_path=constant.reportfile_path
    fo = open(reportfile_path+'/'+filename,"a+")#使用绝对路径 os.chdir在django里会报错
    for item in list_input:
        if item[0] is None:
            pass
        else:
            fo.write(str(item[0]))
            fo.write("\n")
    fo.close()


#获取AWR报告
def getawr(ipadress,port,servicename,dbausername,dbapassword,date,beginhr,endhr,instance_number):
    try:
        connection = Oracle_Conn(dbausername, dbapassword, ipadress, port, servicename)
    except:
        return "Error:数据库无法连接"
    else:
        pass

    #双节点的dbid是一致的
    re_dbid=connection.execsql("select dbid from v$database") #要么报错str要么就是list
    snaptime_begin=str(date)+str(beginhr)#2017032522
    snaptime_end=str(date)+str(endhr)
    snapid_sql='''
        select distinct snap_id from dba_hist_snapshot s
        where to_char(s.end_interval_time,'yyyymmddhh24') in ('{0}','{1}')
        order by 1 '''.format(snaptime_begin,snaptime_end)
    re_snapid=connection.execsql(snapid_sql)

    if isinstance(re_dbid,str) or isinstance(re_snapid,str):
        connection.close_commit()
        return "Error:获取数据库信息异常"
    elif len(re_snapid)!=2:#必须出来2个snap_id 如果1个那么后面生产awr会报错 snap_time_begin和snap_time_end不能相等
        connection.close_commit()
        return "Error:获取SNAPID信息异常"
    else:
        dbid=re_dbid[0][0]
        snapid_begin=re_snapid[0][0]
        snapid_end=re_snapid[1][0]
        awr_sql='''
        select output from 
        table(dbms_workload_repository.awr_report_html({0},{1},{2},{3}, 0 ))
        '''.format(dbid,instance_number,snapid_begin,snapid_end)
        #0 noaddm 8 addm
        #print awr_sql

        re_awr=connection.execsql(awr_sql)
        if isinstance(re_awr,str):
            connection.close_commit()
            return "Error:获取AWR报告异常:"+re_awr
        else:
            awrrpt_name = 'awrrpt_'+ servicename + '_' +str(instance_number)+ '_' + \
                          str(snaptime_begin) + '_' + str(endhr) + '.html'
            #print awrrpt_name
            try:
                makehtml(awrrpt_name,re_awr)
                connection.close_commit()
            except:
                return "Error:AWR报告生成异常"
            else:
                return "Success:请下载后查阅"






#获取ASH报告
def getash(ipadress,port,servicename,dbausername,dbapassword,minutebefore,duration,instance_number):
    try:
        connection = Oracle_Conn(dbausername, dbapassword, ipadress, port, servicename)
    except:
        return "Error:数据库无法连接"
    else:
        pass

    #双节点的dbid是一致的
    re_dbid=connection.execsql("select dbid from v$database") #要么报错str要么就是list
    begintime="SYSDATE-" +str(minutebefore)+"/1440" #SYSDATE-30/1440 
    endtime="SYSDATE-" + str(int(minutebefore)-int(duration))+"/1440"

    if isinstance(re_dbid,str):
        connection.close_commit()
        return "Error:获取数据库信息异常"
    else:
        dbid=re_dbid[0][0]

        ash_sql='''
        select output from 
        table(dbms_workload_repository.ash_report_html( {0},{1},{2},{3}))
        '''.format(dbid,instance_number,begintime,endtime)


        re_ash=connection.execsql(ash_sql)
        if isinstance(re_ash,str):
            connection.close_commit()
            return "Error:获取ASH报告异常:"+re_ash
        else:
            ashrpt_name = 'ashrpt_'+ servicename + '_' +str(instance_number)+ '_minus' + \
                          str(minutebefore) + '_duration' + str(duration) + '.html'
            try:
                makehtml(ashrpt_name,re_ash)
                connection.close_commit()
            except:
                return "Error:ASH报告生成异常"
            else:
                return "Success:请下载后查阅"

