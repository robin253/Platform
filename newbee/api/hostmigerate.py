#!/bin/env python
#coding=utf-8
#created by Jane.Hoo
#created at 08.10.2016
import MySQLdb
import time
import pprint
def test(v_cur_time,v_zabbix_db_msg,v_ansibleui_db_msg):
    var_db_status=''
    var_result=''
    cur_time=v_cur_time
    v_zabbix_host = v_zabbix_db_msg.split(':')[0]
    v_zabbix_port = v_zabbix_db_msg.split(':')[1]
    v_zabbix_db = v_zabbix_db_msg.split(':')[2]
    v_zabbix_user = v_zabbix_db_msg.split(':')[3]
    v_zabbix_passwd = v_zabbix_db_msg.split(':')[4]
    print v_zabbix_host,v_zabbix_port,v_zabbix_user,v_zabbix_passwd,v_zabbix_db

    v_ansibleui_host = v_ansibleui_db_msg.split(':')[0]
    v_ansibleui_port = v_ansibleui_db_msg.split(':')[1]
    v_ansibleui_db = v_ansibleui_db_msg.split(':')[2]
    v_ansibleui_user = v_ansibleui_db_msg.split(':')[3]
    v_ansibleui_passwd = v_ansibleui_db_msg.split(':')[4]
    print v_ansibleui_host,v_ansibleui_port,v_ansibleui_user,v_ansibleui_passwd,v_ansibleui_db

    sql_gethostmsg="select b.host,a.ip,d.name from interface a,hosts b,hosts_groups c ,groups d where a.hostid=b.hostid and b.hostid=c.hostid and c.groupid=d.groupid order by d.name;"
    try:
        conn = MySQLdb.connect(host=v_zabbix_host,user=v_zabbix_user,passwd=v_zabbix_passwd,db=v_zabbix_db,port=int(v_zabbix_port))
        conn2 = MySQLdb.connect(host=v_ansibleui_host ,user=v_ansibleui_user,passwd=v_ansibleui_passwd,db=v_ansibleui_db,port=int(v_ansibleui_port))
        cur = conn.cursor()
        cur2 = conn2.cursor()
        var_db_status = 1
    except Exception as ex:
        print 'The exception is:',ex
        var_db_status = 0
    print 'db status',var_db_status
    if var_db_status == 1 :
        try:
            cur.execute(sql_gethostmsg)
            alldata = cur.fetchall()
            for rec in alldata:
                sql_chekgroup="select * from  api_functiongroup where fun_groupname='"+rec[2]+"';"
                res_chekgroup=cur2.execute(sql_chekgroup)
                print res_chekgroup
                if res_chekgroup == 0:
                    sql_addgroup="insert into api_functiongroup(fun_groupname,created_date,modified_date)values('"+rec[2]+"','"+cur_time+"','"+cur_time+"');"
                    cur2.execute(sql_addgroup)
                    pprint.pprint("functiongroup "+rec[2]+" added success.")
                else:
                    pprint.pprint("functiongroup "+rec[2]+" has exists.")
                sql_checkhost="select 1 from api_host t where t.ip='"+rec[1]+"' and t.hostname='"+rec[0]+"';"
                res_checkhost=cur2.execute(sql_checkhost)
                if res_checkhost == 0:
                    sql_getgroupid="select max(id) from api_functiongroup where fun_groupname='"+rec[2]+"';"
                    sql_gethostid="select max(id)+1 from api_host;"
                    cur2.execute(sql_getgroupid)
                    groupid=str(cur2.fetchall()[0][0])
                    cur2.execute(sql_gethostid)
                    hostid=str(cur2.fetchall()[0][0])
                    sql_addhost="insert into api_host(id,hostname,ip,port,status,host_var,function_group_id,created_date,modified_date)values('"+hostid+"','"+rec[0]+"','"+rec[1]+"','22','1','','"+groupid+"','"+cur_time+"','"+cur_time+"');"
                    cur2.execute(sql_addhost)
                    pprint.pprint("host "+groupid+'='+hostid+'='+rec[1]+" added suceess.")
                else:
                    pprint.pprint("host "+rec[1]+" has exist.")
                    pass
            var_result = 'OK'
        except Exception as e:
            print('Error msg: ' + e)
            var_result = 'NOT OK'
        finally:
            conn2.commit()
            cur.close()
            conn.close()
            conn2.close()
            cur2.close()
    else:
        var_result = 'DB NOT OK'
    return var_result