#!/bin/evn python
#-*- coding: utf-8 -*-

"""
   DB connect and insert function 
"""

__authors__ = [
    '"Lian Shifeng" <lianshifeng-it@bestpay.com.cn>',
]

import MySQLdb
from global_var import * 

def update(table_name,num,mission_id):
	try:
        	conn = MySQLdb.connect(host=DB_HOST,user=DB_USER,passwd=DB_PASSWD,port=3306,db=DB_DATABASE,unix_socket=DB_SOCKET)          
                cur = conn.cursor()
		sql = "replace into %s(id,num) values(%s,%s) " %(table_name,int(mission_id),num)
		cur.execute(sql)
		conn.commit()
                cur.close()
                conn.close()
        except MySQLdb.Error,e:
                print "MySQL Error %d : %s" %(e.args[0],e.args[1])
		


