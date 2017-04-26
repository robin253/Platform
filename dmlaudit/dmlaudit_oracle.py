#!/usr/bin/env python
# -*- coding:utf-8 -*-

from common.connect_oracle import Oracle_Conn
from common import splitor 

import re
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'#防止oracle中文返回出现乱码



class DmlAudit():
    sql_species = {"(^INSERT\s*INTO.*SELECT.*)":"insert_select",        
               "(^INSERT\s*INTO.*)":"insert",  # \s匹配任何空白字符
               "(^UPDATE.*)":"update",#   . 匹配任意字符(除了换行符)
               "(^DELETE.*)":"delete"}#   * 匹配0个或多个的表达式


    def __init__(self,username,password,ip,port,servicename):
        self.connection=Oracle_Conn(username,password,ip,port,servicename)

    def audit(self,sqltext):
        #输入的sqltext可能有很多的换行 有多行注释和单行注释 这不方面确定是什么类型的sql
        #所以要处理一下 当然返回入库的还是原sqltext
        lexerSplitor = splitor.LexerSplitor()
        uncomment_sqltext=lexerSplitor.remove_sqlcomment(sqltext)

        if uncomment_sqltext=='':
            return None  #纯注释语句 直接返回none



        #非sql_species中类型的语句不通过执行
        for key in DmlAudit.sql_species:
            res=re.search(key,uncomment_sqltext,re.IGNORECASE|re.DOTALL)  #正则处理 忽略大小写|Make the '.' special character match any character at all
            if res:
                sqltype=DmlAudit.sql_species[key]
                #print sqltype
                if sqltype=='insert':# 要判断是否是insert select
                    if re.search("(^INSERT\s*INTO.*SELECT.*)",uncomment_sqltext,re.IGNORECASE|re.DOTALL):
                        sqltype='insert_select'
                        break
                    else:
                        break
                else:
                    break
            else:
                sqltype="other"
        #print sqltype

         
        #语法
        if sqltype=='other':
            grammar='invalid'
            gra_failreason="本平台禁止执行非DML语句"
        else:
            gra=self.connection.execsql("explain plan for "+sqltext) #要么报错str要么就是none
            if gra:
                grammar='invalid'
                gra_failreason=gra
            else:
                grammar='valid'
                gra_failreason=''

        #print grammar
        #print gra_failreason



        #执行计划详情 预估行数和执行时间
        sqlplan=[]
        rowaffact=0
        exetime=''
        if grammar=='valid':
            re_sqlplan=self.connection.execsql("select * from table(dbms_xplan.display)") 
            #select * from table(dbms_xplan.display('','','OUTLINE')); 
            for item in re_sqlplan:
                sqlplan.append(item[0])


            if sqltype=='insert':
                tmp_exeplan=re_sqlplan[4][0].split('|')#第一行有效数据 insert一般没有plan hash value
                #insert如果有sequence 那么有plan hash value 这个时候tmp_exeplan长度一般为1
                if len(tmp_exeplan)<8:
                    tmp_exeplan=re_sqlplan[5][0].split('|')#第一行有效数据
            else:
                tmp_exeplan=re_sqlplan[5][0].split('|')#第一行有效数据


            #预估执行时间
            exetime=tmp_exeplan[7].strip()
            if exetime=='': # Bytes有时候不展示 那么7就是空 拿6
                exetime=tmp_exeplan[6].strip()

            #预估影响行数
            evaluate_rows=tmp_exeplan[4]


            rows_value=re.search('\d+',evaluate_rows.strip(),0).group(0)

            rows_unit=''
            if re.search('\D+',evaluate_rows.strip(),0):
               rows_unit=re.search('\D+',evaluate_rows.strip(),0).group(0)
            if rows_unit=='K':
               evaluate_rows=int(rows_value)*1000
            elif rows_unit=='M':
               evaluate_rows=int(rows_value)*1000*1000
            else:
               evaluate_rows=int(rows_value)


            #返回影响行数  如果预估的行数比较少 那么执行并返回精确的行数
            if evaluate_rows>=1000:
                rowaffact=evaluate_rows
            else:
                func_name=sqltype+"_change"
                sqlchange= getattr(DmlAudit,func_name)(uncomment_sqltext)#非注释语句进行改写
                #print sqlchange
                try:
                    rowaffact=int(self.connection.execsql(sqlchange)[0][0])#可能异常不返回数字的str
                except:
                    rowaffact=evaluate_rows
                

        #print rowaffact
        #print exetime
        #print sqlplan 列表

        #最终审核结果 超过10分钟，影响1000行
        if grammar=="invalid":
            audit_status="unqualified"
        elif grammar=="valid" and rowaffact<=1000 and exetime <= '00:10:00':
            audit_status="qualified"
        else:
            audit_status="semi-qualified"

        #print audit_status
        #print sqltext
        #audit_status="semi-qualified"#全部是待评估 用于测试

        re_dict={}
        for i in ['sqltext','grammar','gra_failreason','sqlplan','rowaffact','audit_status','sqltype','exetime']:
            re_dict[i]=locals()[i]
        #print re_dict
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
                return "select * from "+str1+" "+str2
            elif backupflag==0:
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
        delete_position=list_uppersqltext.index("DELETE")
        #print list_uppersqltext[delete_position:]
        
        for item in list_uppersqltext[delete_position:]:
            if item=="FROM":
                position_from=list_uppersqltext.index("FROM")
                break
            elif item=='DELETE' or item=='':
                continue
            else:
                position_from=None
                break
        #print position_from
        if position_from:
            str1=" ".join(list_sqltext[position_from+1:])
            #print str1
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
        auditobject=DmlAudit("xulijia_app","xulijia_app",'192.168.136.88','1521','xljora1')
    except:
        print "wrong"
    else:
        allsqltext="""update t_info_cf_prorata_bill a set a.first_season= '201701', a.current_season= '201701' where a.archive_flag='0' and a.create_uid='admin' and a.sales_mobile_nbr= '18006361247'"""
        lexerSplitor = LexerSplitor()
        for onesql in lexerSplitor.split(allsqltext):
        	print auditobject.update_change(onesql)

        auditobject.close_commit()

    

