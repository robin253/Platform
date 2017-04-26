#!/usr/bin/env python
# -*- coding:utf-8 -*-

from common.connect_mysql import MySQL_Conn
from common import splitor 
import re




class DmlAudit():
    sql_species = {"(^INSERT\s*INTO.*SELECT.*)":"insert_select",             
               "(^INSERT\s*INTO.*)":"insert",
               "(^UPDATE.*)":"update",
               "(^DELETE.*)":"delete"}


    def __init__(self,username,password,ip,port,database):
        self.connection=MySQL_Conn(username,password,ip,port,database)

    def audit(self,sqltext):
        #输入的sqltext可能有很多的换行 有多行注释和单行注释 这不方面确定是什么类型的sql
        #所以要处理一下 当然返回入库的还是原sqltext
        lexerSplitor = splitor.LexerSplitor()
        uncomment_sqltext=lexerSplitor.remove_sqlcomment(sqltext)

        if uncomment_sqltext=='':
            return None  #纯注释语句 直接返回none


        sqltext=uncomment_sqltext #mysql的注释执行有些问题 所以统一去掉注释
        #非sql_species中类型的语句不通过执行
        for key in DmlAudit.sql_species:
            res=re.search(key,uncomment_sqltext,re.IGNORECASE|re.DOTALL)  #正则处理
            if res:
                sqltype=DmlAudit.sql_species[key]
                if sqltype=='insert':# 要判断是否是insert select
                    if re.search("(^INSERT INTO.*SELECT.*)",uncomment_sqltext,re.IGNORECASE|re.DOTALL):
                        sqltype='insert_select'
                    else:
                        break
                else:
                    break
            else:
                sqltype="other"

        #语法
        if sqltype=='other':
            grammar='invalid'
            gra_failreason="本平台禁止执行非DML语句"
            sqlplan=[]
        else:
            gra=self.connection.execsql("explain "+sqltext) #要么报错str要么返回list:执行计划
            if isinstance(gra,str):
                grammar='invalid'
                gra_failreason=gra
                sqlplan=[]
            else:
                grammar='valid'
                gra_failreason=''
                sqlplan=[]


                plan_passflag=0

                if len(gra)>=2 or gra[0][3]=='ALL':  #关联查询 、全表扫描
                    plan_passflag=1
                else:
                    plan_passflag=0



                for item in gra:
                    #item是个元祖
                    tmp_list=[]
                    for i in item:
                        tmp_list.append(str(i))
                    strtmp=' | '.join(tmp_list)
                    sqlplan.append(strtmp)
                sqlplan.insert(0,'id | select_type | table | type | possible_keys | key | key_len | ref | rows | Extra')
        #print sqltype
        #print grammar
        #print gra_failreason
        #print sqlplan

        #执行时间预估 todo
        if grammar=='valid':
            exetime='待开发'
        else:
            exetime=''
        
        #影响行数
        if grammar=='valid':
            func_name=sqltype+"_change"
            sqlchange= getattr(DmlAudit,func_name)(sqltext)
            #print eval(func_name)(sqltext) eval这里不行
            try:
                rowaffact=int(self.connection.execsql(sqlchange)[0][0])#可能异常不返回数字
            except:
                rowaffact=0
        else:
            rowaffact=0


        #print rowaffact
        #print exetime

        #最终审核结果 超过10分钟，影响1000行
        if grammar=="invalid":
            audit_status="unqualified"
        elif grammar=="valid" and rowaffact<=1000 and plan_passflag==0:# and exetime <= '00:10:00':
            audit_status="qualified"
        else:
            audit_status="semi-qualified"

        #print audit_status
        #print sqltext




        re_dict={}
        for i in ['sqltext','grammar','gra_failreason','sqlplan','rowaffact','audit_status','sqltype','exetime']:
            re_dict[i]=locals()[i]
        return re_dict


    def close_commit(self):
        self.connection.close_commit()

    def close_rollback(self):
        self.connection.close_rollback()

    @staticmethod #静态方法 不要self了
    def update_change(sqltext,backupflag=0):
        sqltext=sqltext.replace("\n"," ") #去除换行符号和tab 会造成问题 如果表数据中有\n可能会有问题 最多评估行数不准
        sqltext=sqltext.replace("\t"," ")
        #print sqltext
        list_uppersqltext=sqltext.upper().split(" ")
        #print list_uppersqltext
        position_update=list_uppersqltext.index("UPDATE")
        position_set=list_uppersqltext.index("SET")
    

        try:
            position_where=list_uppersqltext.index("WHERE")
        except:
            position_where=None
        else:
            #有where关键字 一个或者多个
            list_position_where=[]#记录位置
            for i in range(len(list_uppersqltext)):
                if list_uppersqltext[i]=='WHERE':
                    list_position_where.append(i)
            #print list_position_where
    
            position_where=None
            for i in list_position_where:
                tmpstr=' '.join(list_uppersqltext[0:i])
                if tmpstr.count("(")==tmpstr.count(")"):
                    position_where=i
                    break
                else:
                    pass

        list_sqltext=sqltext.split(" ")
        if position_where:
            str1=" ".join(list_sqltext[position_update+1:position_set])
            str2=" ".join(list_sqltext[position_where:])
            if backupflag==1:
                #print "select * from "+str1+" "+str2
                return "select * from "+str1+" "+str2
            elif backupflag==0:
                #print "select count(*) from "+str1+" "+str2
                return "select count(*) from "+str1+" "+str2
            else:
                pass
        else:
            str1=" ".join(list_sqltext[position_update+1:position_set])
            if backupflag==1:
                return "select * from "+str1
            elif backupflag==0:
                return "select count(*) from "+str1
            else:
                pass

    @staticmethod
    def delete_change(sqltext,backupflag=0):
        sqltext=sqltext.replace("\n"," ")
        sqltext=sqltext.replace("\t"," ")

        list_uppersqltext=sqltext.upper().split(" ")
        list_sqltext=sqltext.split(" ")
        for item in list_uppersqltext:
            if item=="FROM":
                position_from=list_uppersqltext.index("FROM")
                break
            elif item=='DELETE' or item=='':
                continue
            else:
                position_from=None
                break
        if position_from:
            str1=" ".join(list_sqltext[position_from+1:])
            if backupflag==0:
                return "select count(*) from "+str1
            elif backupflag==1:
                return "select * from "+str1
            else:
                pass
        else:
            position_delete=list_uppersqltext.index("DELETE")
            str1=" ".join(list_sqltext[position_delete+1:])
            if backupflag==0:
                return "select count(*) from "+str1
            elif backupflag==1:
                return "select * from "+str1
            else:
                pass
    @staticmethod
    def insert_select_change(sqltext):
        sqltext=sqltext.replace("\n"," ")
        sqltext=sqltext.replace("\t"," ")
        list_uppersqltext=sqltext.upper().split(" ")
        list_sqltext=sqltext.split(" ")
        position_from=list_uppersqltext.index("FROM")
        str1=" ".join(list_sqltext[position_from:])
        return "select count(*) "+str1

    @staticmethod
    def insert_change(sqltext):
        return "select 1 from dual"  

    def execsql(self,sqltext):
        return self.connection.execsql(sqltext) 


if __name__ == '__main__':
    try:
        auditobject=DmlAudit("dmlaudit","dmlaudit",'192.168.136.88','3306','dmlaudit')
    except:
        print "wrong"
    else:
        allsqltext="""update test set id=5 where id=888"""
        lexerSplitor = LexerSplitor()
        for onesql in lexerSplitor.split(allsqltext):
            print auditobject.audit(onesql)

        auditobject.close_commit()

    

