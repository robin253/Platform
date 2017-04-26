#!/usr/bin/env python
# -*- coding:utf-8 -*-

#import mysql.connector
#from mysql.connector import errorcode 
#本版本的django连接后台mysql不支持mysql官方的mysql.connector了 
#所以settings配置使用默认的 django.db.backends.mysql 即MySQLdb

#那么这里我们也使用MySQLdb吗？
#缺点
#1.MySQLdb返回和cx_Oracle的不一样 他都是返回tuple的 （虽然这个问题不大 改一下就好了）
#2.MySQLdb不支持MySQL 5.7   这个模块没有人来更新了 
#import MySQLdb
#还是用官方mysql.connector吧

from DBUtils.PooledDB import PooledDB
import mysql.connector as db
from mysql.connector import errorcode

import sys
import threading
#threading用来控制线程 这里用threading.Timer来控制cx_Oracle执行语句的自动超时
#http://stackoverflow.com/questions/2374079/set-database-connection-timeout-in-python


class MySQL_Conn():
    def __init__(self,user,password,host,port,database):
        self.config={'user': user,'password': password,'host': host,'port':port,\
        'database': database,'raise_on_warnings': True}
        try:
            self.pool_inst = PooledDB(creator = db, mincached=1, maxcached=5,
                                host=host, port=int(port),
                                user=user, passwd=password,
                                db=database)
            self.cnx = self.pool_inst.connection()
            # self.cnx=mysql.connector.connect(**self.config)
            #print self.cnx.autocommit
            self.cursor=self.cnx.cursor()

        except Exception as err:
            print self.config
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            sys.exit()
        else:
            #记录自己的process_id
            self.cursor.execute("select connection_id()")
            re=self.cursor.fetchall()
            self.process_id=re[0][0]
            self.cancelsql="kill "+str(self.process_id)
            #print self.cancelsql


    def execsql(self,sqltext,timeout=60):
        res=[]
        try:
            t=threading.Timer(timeout,self.cancel)#超时会执行函数cancel()
            t.start() #开始任务 开始计时
            self.cursor.execute(sqltext)
            t.cancel() #结束任务
        except Exception, errmsg:
            if str(errmsg)=="2013: Lost connection to MySQL server during query":
                return "执行用时超过阀值"+str(timeout)+"秒,系统自动中断"
            else:
                return str(errmsg)
        else:
            try:
                res=self.cursor.fetchall()#如果没有返回结果那么fetchall会报错
            except:
                return None#dml是返回空的
            else:
                return res#返回list


    def close_commit(self):#提交后关闭连接
        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()

    def close_rollback(self):#回滚后关闭连接
        self.cnx.rollback()
        self.cursor.close()
        self.cnx.close()

    def cancel(self):
        self.cnx1=self.pool_inst.connection()
        self.cursor1=self.cnx1.cursor()
        self.cursor1.execute(self.cancelsql)
        self.cursor1.close()
        self.cnx1.close()



if __name__ == '__main__':
    try:
        connection=MySQL_Conn("dmlaudit","dmlaudit",'192.168.136.88','3306','test')
    except:
        print "wrong"
    else:
        #print connection.execsql("SET autocommit=off")
        print connection.execsql("update t2 set id=777")
        print connection.execsql("select * from t_database_info")
        print connection.execsql("update t12 set id=777")


        #InnoDB关于在出现锁等待的时候，会根据参数innodb_lock_wait_timeout的配置，进行timeout的操作
        #1205 (HY000): Lock wait timeout exceeded; try restarting transaction
        #但如果是长查询就不能控制了
        ##mysql没有cx_Oracle那个cancel 所以要新建一个连接 然后杀当前连接 之前记录了当前process_id
        ##杀掉就自己回滚了
