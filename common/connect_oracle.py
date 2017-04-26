#!/usr/bin/env python
# -*- coding:utf-8 -*-

import cx_Oracle as db
import sys
#from DBUtils.PooledDB import PooledDB

import threading
#threading用来控制线程 这里用threading.Timer来控制cx_Oracle执行语句的自动超时
#http://stackoverflow.com/questions/2374079/set-database-connection-timeout-in-python

class Oracle_Conn():
    def __init__(self,username,password,ip,port,servicename):
        #try:
        #    dsn = "{0}:{1}/{2}".format(ip,port,servicename)
        #    self.pool_inst = PooledDB(creator=db, mincached=1, maxcached=5,
        #                       user=username, password=password, dsn=dsn)
        #    self.con = self.pool_inst.connection()
        #    self.cur=self.con.cursor()
        #except Exception,errmsg:
        #    sys.exit()
        #else:
        #    pass

        try:
            self.con=db.connect("{0}/{1}@{2}:{3}/{4}".format(username, password, ip,port, servicename))
            self.cur=db.Cursor(self.con)
        except Exception,errmsg:
            #print self.ip+":"+str(self.port)+"/"+self.servicename+" can not be connected!  \n "+str(errmsg)
            sys.exit()
        else:
            pass

    def execsql(self,sqltext,timeout=120):
        try:
            t=threading.Timer(timeout,self.cancel)#超时会执行函数cancel()
            t.start() #开始任务 开始计时
            self.cur.execute(sqltext)
            t.cancel() #结束任务
        except Exception, errmsg:
            #语句执行失败或者超时
            if str(errmsg).startswith("ORA-01013"):#ORA-01013: user requested cancel of current operation\n
                return "执行用时超过阀值"+str(timeout)+"秒,系统自动中断"
            else:
                return str(errmsg)
        else:
            #语句执行成功
            #(fetchone出来是一个元祖 返回第一行)  fetchall返回多行 是列表 列表的元素是元祖
            #dml和explain plan都是返回None
            try:
                res=self.cur.fetchall()
            except:
                # 如果没有返回结果那么fetchall会报错
            	return None
            else:
            	return res


    def close_commit(self):#提交后关闭连接
        self.con.commit()
        self.cur.close()
        self.con.close()

    def close_rollback(self):#回滚后关闭连接
        self.con.rollback()
        self.cur.close()
        self.con.close()

    def cancel(self):
        self.con.cancel()#取消正在执行的sql 不做提交和回滚动作



if __name__ == '__main__':
    try:
       connection=Oracle_Conn("xulijia","xulijia",'192.168.136.88','1521','xljora1')
    except:
        print "connect wrong"
    else:
        #print connection.execsql("select 1 from dual")
        print connection.execsql("update t2 set id=11 where id=1")


