#!/bin/env python
# coding=UTF-8
import os
from re import search
import re
import copy

from parenthesis import remove_cont_parenthesis    #删除字符串中所有括号和括号里面的内容 
from parenthesis import find_cont_firstparenthesis #返回字符串中第一个括号组中的内容 

from str_manipulation import removespaces #连续两个空格及以上的只保留一个 并删除字符串前后的所有空格 
from str_manipulation import findallstr #判断字符串中是否有指定的一个或者多个字符 全部找到返回1  否则返回0 
from str_manipulation import findanystr #判断字符串中是否有指定的一个或者多个字符 只要找到一个或以上则返回1 否则返回0 
from str_manipulation import findstrnext  #找字符串某个关键词后面的词 空格作为词的分隔符号  返回0那么说明不存在关键词或者关键词后面没有词了 
from str_manipulation import findstrbefore#找字符串某个关键词前面的词 空格作为词的分隔符号  返回0那么说明不存在关键词或者关键词前面没有词了 
from str_manipulation import bracklet_split #对字符串以，分隔为列表，可避免k1,k2(k3,k4),k5这种情况的分割异常 [k1,k2(k3,k4),k5] 
from str_manipulation import remove_comma_childstr #对字符串以，分隔为列表,如果列表元素中有相关关键字那么删除这个元素 返回字符串
from str_manipulation import namesplit     #将字符串owner.object_name 以.分隔并返回object_name  
from str_manipulation import namecheck     #检查对象名长度不超过30并不能用数字开头  

from list_manipulation import delRepeat    #删除列表中的重复项  相同项只保留一个 
from list_manipulation import analyseRepeat #统计列表中的重复项 返回一个字典 
from list_manipulation import comparetwolists   #对比两个列表,将差异返回为一个元祖（两个列表） 输入的列表不要有重复项 
from list_manipulation import removesomeitems #删除列表中的一些项，删除项来自列表remove_list  符合这些项的全部删除 
from list_manipulation import removetheoneafter #删除列表中某个项的后面一项 

from dict_manipulation import mergedict #将两个字典的内容合并

from dealsqltext import dealsqltext#处理待审核的sql文本格式 


  #####################
#Part1 一些全局变量定义#
  #####################

def init_variable():

    global ct_tabnames
    ct_tabnames=[]          #记录建表语句的所有表名  
    global ct_part_tabnames
    ct_part_tabnames=[]     #记录建表语句中的分区表的表名
    global dict_ct_tab_col
    dict_ct_tab_col={}      #记录表和表的列  {'T1': ['COL1', 'COL2']} add col 、rename col 、drop col的语句也会将表和列加入这个字典
    global dict_ct_partab
    dict_ct_partab={}       #记录分区表和对应分区列、分区类型

    global ci_indnames
    ci_indnames=[]         #记录索引名 （表名.索引名）
    global dict_ci_ind_col
    dict_ci_ind_col={}     #记录索引和对应的列 (表名.索引名:col1,col2)

    global cs_seqnames
    cs_seqnames=[]          #记录序列名

    global comtab_tabnames
    comtab_tabnames=[]          #记录表注释语句对应的表名
    global comcol_tabnames
    comcol_tabnames = []         #记录列注释语句对应的表名
    global dict_comcol_tab_col
    dict_comcol_tab_col = {}     #记录列注释语句的表和表的列  {'T1': ['COL1', 'COL2']}

    global truncate_tabnames
    truncate_tabnames=[]   #记录截断表语句的表名

    global at_pknames
    at_pknames=[]                #记录创建主键语句中的主键名（表名.主键名）
    global at_pktabnames
    at_pktabnames=[]             #记录创建主键语句中的表名
    global dict_at_pk_col
    dict_at_pk_col={}            #记录创建主键语句中的主键名和对应的列 (表名.主键名:col1)

    global at_uknames
    at_uknames=[]      #记录创建唯一约束语句中的约束名（表名.约束名）
    global dict_at_uk_col
    dict_at_uk_col={}  #记录创建唯一约束语句中的约束名和对应的列 （表名.约束名：col1,col2)
    global sqltype_count

    #sql语句类型统计 共计18种
    sqltype_count={'createtab_select':0,'createtab':0,'createidx':0,'createseq':0,'commenttab':0,'commentcol':0,
        'truncate':0,'addpk':0,'adduk':0,'addcol':0,'renamecol':0,'modifycol':0,'dropcol':0,'dropconst':0,
        'droptab':0,'dropidx':0,'dropseq':0,'othersql':0}



  #####################
#Part2 入口函数#
  #####################

#对sql语句进行分类
def classify_sql(sql_str):
    #sql_species是一个字典 记录划分sql类型的正则表达式信息
    sql_species = {"(^CREATE TABLE.*AS SELECT.*)":"createtab_select",
               "(^CREATE TABLE.*)":"createtab",
               "(^CREATE.*INDEX.*)":"createidx",#(^CREATE UNIQUE INDEX.*)
               "(^CREATE SEQUENCE.*)":"createseq",  
               "(^COMMENT ON TABLE.*)":"commenttab",
               "(^COMMENT ON COLUMN.*)":"commentcol",
               "(^TRUNCATE.*)":"truncate",
               "(^ALTER TABLE.*)":"altertab_species",
               "(^DROP.*)":"drop_species"
               }
    for key in sql_species:
        res=search(key,sql_str,re.DOTALL|re.IGNORECASE)  #正则处理
        if res:
            return sql_species[key]
        else:
            continue
    return "othersql"


def drop_species(drop_str):
    #drop_species细分
    drop_filter = {
    "(^DROP TABLE.*)":"droptab", 
    "(^DROP INDEX.*)": "dropidx",
    "(^DROP SEQUENCE.*)":"dropseq" }
    for key in drop_filter:
        res=search(key,drop_str,re.DOTALL|re.IGNORECASE)  #正则处理
        if res:
            return drop_filter[key]
        else:
            continue
    return "othersql"

def altertab_species(alter_str):
    #altertab_species细分
    altertab_filter = {"(^ALTER TABLE.*ADD CONSTRAINT.*PRIMARY KEY.*)":"addpk",
                  "(^ALTER TABLE.*ADD CONSTRAINT.*UNIQUE.*)":"adduk",
                 "(^ALTER TABLE.*ADD.*)":"addcol",
                 "(^ALTER TABLE.*RENAME COLUMN.*)":"renamecol",
                 "(^ALTER TABLE.*MODIFY.*)":"modifycol",
                 "(^ALTER TABLE.*DROP COLUMN.*)":"dropcol",
                 "(^ALTER TABLE.*DROP CONSTRAINT.*)":"dropconst"
                 }
    for key in altertab_filter:
        res=search(key,alter_str,re.DOTALL|re.IGNORECASE)  #正则处理
        if res:
            return altertab_filter[key]
        else:
            continue
    return "othersql" 


#审核sql主功能函数
def process_sqlfile(sqltext,dict_config_input):
    global dict_config
    dict_config=dict_config_input
    init_variable() 
    list_auditresult=[]
    fsqlfinal = dealsqltext(sqltext)

    
    for sql_str in fsqlfinal:
        sql_check=classify_sql(sql_str)
        if sql_check=='altertab_species':
            sql_check = altertab_species(sql_str)
        elif sql_check=='drop_species':
            sql_check = drop_species(sql_str)
        #print sql_str,sql_check        #获取了sql语句的类型  详见part1
        rest = eval(sql_check)(sql_str)
        #根据sql语句的类型 进行函数处理 统一返回{'status':A,'type':'B','content':'C','results':[]}
        

        if rest!={}:
            #进行语句类型计数
            sqltype=rest['type']
            if sqltype_count.has_key(sqltype):
                sqltype_count[sqltype]+=1
            #各类型语句审核结果
            list_auditresult.append(rest)
        else:
            pass


    #汇总类审核结果
    list_auditsummary = summary()
    list_auditresult.extend(list_auditsummary)
    #返回
    return list_auditresult




  #####################
#Part3 审核功能函数#
  #####################




def createtab_select(sql_str):
    audit_ct = []
    flag = 0

    #利用正则表达式去除处于TABLE和AS之间的表名
    tmp_str = re.search("(?<=TABLE) .* (?=AS)",sql_str,re.DOTALL|re.IGNORECASE)
    if tmp_str==None:
        seqerr=[]
        seqerr.append("错误：语法出错,无法正常解析；")
        dictoutput={'status':2,'type':'createtab_select','content':sql_str,'results':seqerr}
        return dictoutput
    else:
        ct_tabname = tmp_str.group().strip()
        ct_tabname = ct_tabname.split('.')[-1]
        ct_tabname=ct_tabname.upper()
        #print ct_tabname

    #判断表名相关
    if not ct_tabname.startswith(dict_config['tabname_config']):#配置项
        audit_ct.append("表名"+ct_tabname+"不符合规范,请以"+dict_config['tabname_config']+"开头；")
        flag=1

    if namecheck(ct_tabname):
        audit_ct.append("错误：表名"+ct_tabname+namecheck(ct_tabname)+"；")
        flag=1


    #重复创建表处理
    if ct_tabname in ct_tabnames:
        audit_ct.append("错误：表"+ct_tabname+"重复创建；")
        flag=1
    else:
        ct_tabnames.append(ct_tabname)
    #输出结果
    if flag==1:
        dictoutput={'status':1,'type':'createtab_select','content':sql_str,'results':audit_ct}
    else:
        audit_ct = ["符合规范，审核通过"]
        dictoutput={'status':0,'type':'createtab_select','content':sql_str,'results':audit_ct}
    return dictoutput





def createtab(sql_str):
    listres = []
    audit_ct=[]
    flag=0
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    ct_tabname=findstrnext(sql_str,'TABLE')#抽取表名 
    a=find_cont_firstparenthesis(sql_str)#利用函数 获取第一个括号中的信息 
    n=a[0]                               #获取标志位
    m=a[3]                               #获取实际的内容  ID NUMBER,COL2 VARCHAR2(20),COL3 VARCHAR2(30) not null,COL4 VARCHAR2(30),constraint CODE primary key (id)
    if ct_tabname==0 or n==1:
        seqerr=[]
        seqerr.append("错误：语法出错,无法正常解析；")
        dictoutput={'status':2,'type':'createtab','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        ct_tabname = namesplit(ct_tabname)#获取表名
        #print ct_tabname

        
        #提取主键   出现这种格式typecode char(2),constraint CODE PRIMARY KEY (typecode) 或者typecode char(2),PRIMARY KEY (typecode)是不规范的要报错的
        t_list = bracklet_split(m)#以，为分隔符将字符串转为列表
        primary_key_item=""
        for item in t_list:
            if item.find('PRIMARY KEY')!=-1:
                primary_key_item = item
                break
        if primary_key_item!="":
            #primary_key_info=find_cont_firstparenthesis(primary_key_item)
            #primary_key_col=primary_key_info[3]#主键列信息
            flag=1
            audit_ct.append("请不要在建表语句中定义主键，主键需单独添加；")
            

        
        
        #将列信息和字段类型提出
        #出现这种格式typecode char(2),constraint CODE PRIMARY KEY (typecode) 或者typecode char(2),PRIMARY KEY (typecode)
        #对字符串以，分隔为列表,如果列表元素中有PRIMARY KEY关键字那么删除这个元素 返回字符串   
        mm=remove_comma_childstr(m,"PRIMARY KEY") 

        #删除字符串中所有括号和括号里面的内容
        mmm=remove_cont_parenthesis(mm)

        #继续处理获取列名和所有字段类型 需要把not null default 和default值等关键字去掉
        mmm_tmpstr=removespaces(mmm.replace(","," "))  ##将逗号替换成空格 删除字符串中多余的空格 
        list_colinfo=mmm_tmpstr.split(' ')  #转为列表
        list_colinfo2=removetheoneafter(list_colinfo,'DEFAULT') #删除default后面的元素
        listfinal=removesomeitems(list_colinfo2,['NOT','NULL','DEFAULT']) #删除NOT NULL DEFAULT元素
        #print listfinal
        
        tmpnum=0
        list_col=[]
        list_datatype=[]
        for i in listfinal:
            if tmpnum%2==1:
                list_datatype.append(i)
            else:
                list_col.append(i)
            tmpnum=tmpnum+1

        tmp_cols=','.join(list_col)       
        #print tmp_cols  #输出所有列名 字符串形式 COL1,COL2,COL3
        #print list_datatype # 输出所有字段类型 列表形式

        
        #处理分区表的情况
        partition_flag=0
        partition_type="" #分区类型
        y="" #分区字段
        if sql_str.find('PARTITION BY')!=-1:
            partition_flag=1
            tmpline=sql_str[sql_str.find('PARTITION BY'):]
            partition_type=findstrnext(tmpline,'BY')#获取分区类型
            b=find_cont_firstparenthesis(tmpline)   #获取第一个括号中的信息
            x=b[0]                                  #获取标志位
            y=b[3]                                  #获取分区字段
            y=removespaces(y)
            if partition_type==0 or x==1:
                seqerr=[]
                seqerr.append("错误：分区语法出错；")
                dictoutput={'status':2,'type':'createtab','content':orig_sql_str,'results':seqerr}
                return dictoutput
            else:

                if partition_type!='HASH' and partition_type!='LIST' and partition_type!='RANGE': #如果分区类型不是这三个那么报错
                    seqerr=[]
                    seqerr.append("错误：分区类型不存在；")
                    dictoutput={'status':2,'type':'createtab','content':orig_sql_str,'results':seqerr}
                    return dictoutput
                if y.count(",")>0:                     #分区列只能是单列
                    seqerr=[]
                    seqerr.append("错误：分区列只能是单列；")
                    dictoutput={'status':2,'type':'createtab','content':orig_sql_str,'results':seqerr}
                    return dictoutput
                if tmp_cols.find(y)==-1:               #分区列必须是建表中定义的列
                    seqerr=[]
                    seqerr.append("错误：分区列不存在；")
                    dictoutput={'status':2,'type':'createtab','content':orig_sql_str,'results':seqerr}
                    return dictoutput
                
                    

        #处理重复列名
        tmp_list=tmp_cols.split(",")
        #for item in tmp_list:
        #    print item
        dict_tmp_ct_cols=analyseRepeat(tmp_list)
        for key2 in dict_tmp_ct_cols:
            if dict_tmp_ct_cols[key2]>1:
                audit_ct.append("错误：表"+ct_tabname+"重复创建列"+key2+" "+str(dict_tmp_ct_cols[key2])+"次；")
                flag=1


    #判断表名相关
    if not ct_tabname.startswith(dict_config['tabname_config']):#配置项
        audit_ct.append("表名"+ct_tabname+"不符合规范,请以"+dict_config['tabname_config']+"开头；")
        flag=1

    if namecheck(ct_tabname):
        audit_ct.append("错误：表名"+ct_tabname+namecheck(ct_tabname)+"；")
        flag=1

    #判断字段类型    
    wrongcoltype = removesomeitems(list_datatype,dict_config['coltype_standard']) #配置项 去除合规的字段类型
    wrongcoltype=delRepeat(wrongcoltype)
    str_wrongcoltype='、'.join(wrongcoltype)
    #print str_wrongcoltype
    if wrongcoltype != []:
        audit_ct.append("使用了"+str_wrongcoltype+"类型的字段,请尽量使用varchar2、char,number,date四种字段类型；")
        flag=1

    noexistscoltype=removesomeitems(list_datatype,dict_config['coltype_total']) #配置项
    if noexistscoltype!=[]:
        audit_ct.append('、'.join(noexistscoltype)+"可能是无效的字段类型；")
        flag=1

    #表空间
    if findanystr(sql_str,'TABLESPACE'):
        tabspacename=findstrnext(sql_str,'TABLESPACE')
        if tabspacename==0:
            audit_ct.append("表空间为空，该模块应使用 %s 表空间；" %dict_config['data_tbs'])
            flag=1
        elif tabspacename!=dict_config['data_tbs']:
            #print tabspacename
            audit_ct.append("表空间不准确，该模块应使用 %s 表空间；" %dict_config['data_tbs'])
            flag=1
    else:
        audit_ct.append("没有指定表空间, 该模块使用 %s 表空间；" %dict_config['data_tbs'])
        flag=1


        
    #重复创建表处理
    if ct_tabname in ct_tabnames:
        audit_ct.append("错误：表"+ct_tabname+"重复创建,本句忽略；")
        flag=1
    else:
        ct_tabnames.append(ct_tabname)
        dict_ct_tab_col[ct_tabname]=dict_tmp_ct_cols.keys()#记录表和列

        if partition_flag==1:
            dict_ct_partab[ct_tabname]=partition_type+":"+y
            ct_part_tabnames.append(ct_tabname)

        #print ct_tabnames
        #print dict_ct_tab_col
        #print ct_part_tabnames
        #print dict_ct_partab
        

            

    #输出结果
    if flag==1:
        dictoutput={'status':1,'type':'createtab','content':orig_sql_str,'results':audit_ct}
    else:
        audit_ct = ["符合规范，审核通过；"]
        dictoutput={'status':0,'type':'createtab','content':orig_sql_str,'results':audit_ct}
    return dictoutput



def createidx(sql_str):
    dictoutput={}
    audit_ci=[]
    flag=0
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    idxname=findstrnext(sql_str,'INDEX') #抽取索引名
    tabname=findstrnext(sql_str,'ON')    #抽取表名  create index I_T1 on T1(COL1,COL2)  这里T1和（默认加了一个空格
    a=find_cont_firstparenthesis(sql_str)#利用函数 获取第一个括号中的信息
    n=a[0]                            #获取标志位
    m=a[3]                            #获取第一个括号中的信息
    m=removespaces(m)
    if idxname==0 or tabname==0 or n==1:
        seqerr=[]
        seqerr.append("语法错误；")
        dictoutput={'status':2,'type':'createidx','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        tabname = namesplit(tabname)#获取表名
        idxname = namesplit(idxname)#获取索引名

        #分离索引字段，去除索引字段中的ASC DESC等约束条件
        ind_list=[]
        m=m.replace(","," ") #将逗号替换成空格
        m=removespaces(m)  #删除字符串中多余的空格
        #print m
        list_m=m.split(' ')  #转为列表
        ind_list=removesomeitems(list_m,['ASC','DESC']) #删除ASC DESC元素
        #print ind_list

        #一个索引中的索引列名重复 那么会报错
        dict_tmp_ci_cols=analyseRepeat(ind_list)
        for key2 in dict_tmp_ci_cols:
            if dict_tmp_ci_cols[key2]>1:
                audit_ci.append("索引"+idxname+"重复出现列"+key2+""+str(dict_tmp_ci_cols[key2])+"次；")
                flag=1
        #删除重复的列名
        ind_list=delRepeat(ind_list)
        new_m=','.join(ind_list)

        #索引前导列判断
        firstcol=ind_list[0]  #前导列

        if findanystr(firstcol,'TIME')==1 or findanystr(firstcol,'DATE')==1: #判断是否时间字段
            audit_ci.append("索引"+idxname+"的前导列"+firstcol+"涉及时间字段,容易发生问题；")
            flag=1

        #判断是否分区字段
        try:
            tmp_ct_partab=dict_ct_partab[tabname]
        except:
            pass
        else:
            tmp_ct_partab=tmp_ct_partab.replace(":",": ")
            tmp_ct_partab=findstrnext(tmp_ct_partab,":")    #获取分区列
            if firstcol==tmp_ct_partab:
                audit_ci.append("索引"+idxname+"的前导列"+firstcol+"涉及分区表的分区字段,请注意；")
                flag=1

        #索引列是否存在的判断（跟表的列进行对比）# print dict_ct_tab_col
        try:
            tmp_list_tabcols=dict_ct_tab_col[tabname]
        except:
            audit_ci.append("在文本中，没有找到索引"+idxname+"所在的表"+tabname+"的创建语句；")
            flag=1
            if findallstr(sql_str,'ONLINE'):
                pass
            else:
                audit_ci.append("为已有表创建索引，需添加online关键字在线创建；")

        else:
            tmp_list_tabcols=dict_ct_tab_col[tabname]  #表的全部列 tmp_list_tabcols
            #全部索引列tmp_list
            re=comparetwolists(tmp_list_tabcols,ind_list)
            if re[1]!=[]: #tmp_list 有多余的值 就是索引列不存在
                noexistscol=','.join(re[1])
                audit_ci.append("索引列"+noexistscol+"不存在,请检查创建表"+tabname+"的语句中是否存在该字段；")
                flag=1
        #print tabname     #表名处理完毕
        #print idxname     #索引名处理完毕
        #print new_m       #索引列处理完毕 字符串 各列用,分隔


        #判断索引名相关       
        if idxname.startswith(dict_config['indname_config']) or \
           idxname.startswith(dict_config['uniqindname_config']):
            pass
        else:
            audit_ci.append("索引名"+idxname+"不符合规范,请以"+dict_config['indname_config']+\
                             "或者"+dict_config['uniqindname_config']+"开头；")
            flag=1

        if namecheck(idxname):
            audit_ci.append("错误：索引名"+idxname+namecheck(idxname)+"；")
            flag=1
            
        b=new_m.count(",")+1             #获取索引列的个数 
        if b>dict_config['ind_max_colnum']:
            audit_ci.append("索引"+idxname+"联合列数量大于"+str(dict_config['ind_max_colnum'])+",顺序:"+new_m+",请注意；")
            flag=1

        if ct_part_tabnames.count(tabname)>0: #看这个表是分区表
            if not findanystr(sql_str,'LOCAL'):
                audit_ci.append("分区表上请不要使用全局索引"+idxname+",请添加local关键字；")
                flag=1

    #表空间
    if findanystr(sql_str,'TABLESPACE'):
        tabspacename=findstrnext(sql_str,'TABLESPACE')
        if tabspacename==0:
            audit_ci.append("表空间为空，该模块应使用 %s 表空间；" %dict_config['ind_tbs'])
            flag=1
        elif tabspacename!=dict_config['ind_tbs']:
            audit_ci.append("表空间不准确，该模块应使用 %s 表空间；" %dict_config['ind_tbs'])
            flag=1
    else:
        audit_ci.append("没有指定索引表空间, 该模块使用 %s 表空间；" %dict_config['ind_tbs'])
        flag=1
        



    if findallstr(sql_str,'PARALLEL'):
        audit_ci.append("请不要打开并行创建索引；")
        flag=1
        
    #重复建索引处理
    tabindname = tabname+"."+idxname
    if tabindname in ci_indnames:
        audit_ci.append("错误：索引"+tabindname+"已存在；")
        flag = 1
    else:
        ci_indnames.append(tabindname)
        dict_ci_ind_col[tabindname]=new_m #非常重要
        #print dict_ci_ind_col

    if flag==1:
        dictoutput={'status':1,'type':'createidx','content':orig_sql_str,'results':audit_ci}
    else:
        audit_ci = ["符合规范，审核通过"]
        dictoutput={'status':0,'type':'createidx','content':orig_sql_str,'results':audit_ci}
    return dictoutput






def createseq(sql_str):
    dictoutput={}
    audit_cs=[]
    flag=0
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    seqstr=findstrnext(sql_str,'SEQUENCE')
    if seqstr==0:
        seqerr=[]
        seqerr.append("语法错误；")
        dictoutput={'status':2,'type':'createseq','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        seqname = namesplit(seqstr)#获取序列名

        #审核序列名相关
        if not seqname.startswith(dict_config['seqname_config']): #配置项
            audit_cs.append("序列名"+seqname+"不符合规范,请以"+dict_config['seqname_config']+"开头；")
            flag=1

        if namecheck(seqname):
            audit_cs.append("错误：序列名"+seqname+namecheck(seqname)+"；")
            flag=1
        
        #序列名可能有order关键字 需要排除
        if findanystr(sql_str.replace(seqname,''),'ORDER')==1 and findanystr(sql_str.replace(seqname,''),'NOORDER')==0:
            audit_cs.append("请不要使用ORDER属性；")
            flag=1
         #审核参数相关
        if findstrnext(sql_str,'CACHE'):
            tmpstr=findstrnext(sql_str,'CACHE')
            try:
                num=int(tmpstr)
            except:
                audit_cs.append("没有指定序列的CACHE值；")
                flag=1
            else:
                if num>=int(dict_config['seqcache']): #配置项
                    pass
                else:
                    audit_cs.append("指定序列CACHE值小于阀值"+str(dict_config['seqcache'])+"；")
                    flag=1
        else:
            audit_cs.append("没有指定序列的CACHE值；")
            flag=1

        if findanystr(sql_str,'CYCLE') and (not findanystr(sql_str,'NOCYCLE')):
            audit_cs.append("使用了CYCLE属性,一般用于生成逻辑主键；")
            #flag=1 这个是通过的

        #重复创建序列处理
        if seqname in cs_seqnames:
            audit_cs.append("错误：序列"+seqname+"重复创建；")
            flag = 1
        else:
            cs_seqnames.append(seqname)

        #输出结果
        if flag==1:
            dictoutput={'status':1,'type':'createseq','content':orig_sql_str,'results':audit_cs}
        else:
            audit_str = ["符合规范，审核通过；"]
            dictoutput = {'status':0,'type':'createseq','content':orig_sql_str,'results':audit_str}
        return dictoutput
    
    


def commenttab(sql_str):
    dictoutput={}
    audit_co=[]
    flag=0
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    co_tabname=findstrnext(sql_str,'TABLE') #抽取表名
    co_content=findstrnext(sql_str,'IS')  #抽取注释内容
    co_cont=sql_str.count("'")
    if co_cont==0:
        co_cont=sql_str.count('"')

    if co_tabname==0 or co_content==0 or co_cont!=2:
        seqerr=[]
        seqerr.append("语法错误；")
        dictoutput={'status':2,'type':'commenttab','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        if sql_str.find("''")!=-1  or sql_str.find('""')!=-1:
            flag=1
            audit_co.append("注释内容为空；")

    co_tabname = namesplit(co_tabname)#获取表名
    
    #和建表语句进行对比 看是否有建表语句
    if co_tabname not in ct_tabnames:
        audit_co.append("文本中无表 %s 的正确建表语句；"%co_tabname)
        flag = 1
        
    #重复表注释处理
    if co_tabname in comtab_tabnames:
        audit_co.append("表 %s 重复注释；"%co_tabname)
        flag = 1
    else:
        comtab_tabnames.append(co_tabname)
        
    if flag==1:
        dictoutput={'status':1,'type':'commenttab','content':orig_sql_str,'results':audit_co}
    else:
        audit_co=["符合规范，审核通过；"]
        dictoutput={'status':0,'type':'commenttab','content':orig_sql_str,'results':audit_co}
    return dictoutput


def commentcol(sql_str):
    dict_tab_col={}
    dictoutput={}
    audit_col=[]
    flag=0
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    col_tabcol=findstrnext(sql_str,'COLUMN') #抽取表名和列名
    col_commenttabntent=findstrnext(sql_str,'IS')  #抽取注释内容
    col_commenttabnt=sql_str.count("'")
    if col_commenttabnt==0:
        col_commenttabnt=sql_str.count('"')
    if col_tabcol==0 or col_commenttabntent==0 or col_commenttabnt!=2:
        seqerr=[]
        seqerr.append("语法错误；")
        dictoutput={'status':2,'type':'commentcol','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        if sql_str.find("''")!=-1  or sql_str.find('""')!=-1:
            flag=1
            audit_col.append("注释内容为空；")

        if col_tabcol.find(".")==-1:    #处理表名和列名
            pass
        elif col_tabcol.count(".")==1:
            position=col_tabcol.find(".")
            col_tabname=col_tabcol[0:position] #表名
            col_col=col_tabcol[position+1:]#列名
        elif col_tabcol.count(".")==2:
            tmpposition=col_tabcol.find(".")
            tmpcolstr=col_tabcol[tmpposition+1:]
            #print tmpcolstr
            position2=tmpcolstr.find(".")
            col_tabname=tmpcolstr[0:position2] #表名
            col_col=tmpcolstr[position2+1:] #列名
        #print col_tabname
        #print col_col



        #和建表语句进行对比 看是否有建表语句 是否有对应的列
        if col_tabname not in dict_ct_tab_col.keys():
            audit_col.append("文本中无表 %s 的正确建表语句,请检查；"%col_tabname)
            flag=1
        elif col_col not in dict_ct_tab_col[col_tabname]:
            audit_col.append("表 %s 中不存在%s列 ,请检查建表语句；"%(col_tabname,col_col))
            flag=1
        #重复列注释处理
        if dict_comcol_tab_col.has_key(col_tabname):
            if col_col in dict_comcol_tab_col[col_tabname]:
                audit_col.append("表 %s 的列 %s 重复注释；"%(col_tabname,col_col))
                flag=1
            else:
                dict_comcol_tab_col[col_tabname].append(col_col)
        else:
            dict_comcol_tab_col[col_tabname]=[col_col]


        if col_tabname in comcol_tabnames:
            pass
        else:
            comcol_tabnames.append(col_tabname)
            
        #print comcol_tabnames     
        #print dict_comcol_tab_col

    #结果输出   
    if flag==1:
        dictoutput={'status':1, 'type':'commentcol', 'content':orig_sql_str, 'results':audit_col}
    else:
        audit_col=["符合规范，审核通过；"]
        dictoutput={'status':0, 'type':'commentcol', 'content':orig_sql_str, 'results':audit_col}
    return dictoutput
    
    

def truncate(sql_str):
    dictoutput={}
    audit_truncate=[]
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    truncate_tab=findstrnext(sql_str,'TABLE')

    if truncate_tab==0:
        seqerr=[]
        seqerr.append("错误：语法出错；")
        dictoutput={'status':2,'type':'truncate','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        truncate_tab = namesplit(truncate_tab)#获取表名

        #print truncate_tab
        truncate_tabnames.append(truncate_tab)

    audit_truncate.append("TRUNCATE表"+truncate_tab+"执行后无法回退，请与DBA沟通；")
    dictoutput={'status':1,'type':'truncate','content':orig_sql_str,'results':audit_truncate}
    return dictoutput
        
        

    


def othersql(sql_str):
    audit_others=[]
    dictoutput={}
    audit_others.append("系统目前不支持该类型语句的审核,请与DBA沟通；")
    dictoutput={'status':1,'type':'othersql','content':sql_str,'results':audit_others}
    return dictoutput
     
    



def addpk(sql_str):
    dictoutput={}
    audit_at=[]
    flag=0
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    pkname=findstrbefore(sql_str,'PRIMARY') #抽取主键名
    tabname=findstrnext(sql_str,'TABLE')    #抽取表名
    a=find_cont_firstparenthesis(sql_str)   #利用函数 获取第一个括号中的信息
    n=a[0]                               #获取标志位
    m=a[3]                               #获取第一个括号中的信息
    #print m
    tmpm=m.replace(","," ") #将逗号替换掉
    tmpm=removespaces(tmpm)  #删除字符串中多余的空格
    li_tmpm=tmpm.split(' ')    #转为列表
    m=','.join(li_tmpm) #获取列信息 转为字符串
    #print m

    if pkname==0 or tabname==0 or n==1:
        seqerr=[]
        seqerr.append("语法错误；")
        dictoutput={'status':2,'type':'addpk','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        tabname = namesplit(tabname)#获取表名
        #print tabname
        pkname = namesplit(pkname)#获取主键名
        #print pkname

        #一个主键索引中的索引列名重复 那么会报错
        tmp_list=m.split(",")
        dict_tmp_ci_cols=analyseRepeat(tmp_list)
        for key2 in dict_tmp_ci_cols:
            if dict_tmp_ci_cols[key2]>1:
                audit_at.append("主键索引"+pkname+"重复出现列"+key2+""+str(dict_tmp_ci_cols[key2])+"次；")
                flag=1
        #删除重复的列名
        tmp_list=delRepeat(tmp_list)
        new_m=','.join(tmp_list)
        #print new_m

        #索引前导列判断
        firstcol=tmp_list[0]  #前导列

        if findanystr(firstcol,'TIME')==1 or findanystr(firstcol,'DATE')==1: #判断是否时间字段
            audit_at.append("主键索引"+pkname+"的前导列"+firstcol+"涉及时间字段,不合理；")
            flag=1

        #判断是否分区字段
        try:
            tmp_ct_partab=dict_ct_partab[tabname]
        except:
            pass
        else:
            tmp_ct_partab=dict_ct_partab[tabname]
            tmp_ct_partab=tmp_ct_partab.replace(":",": ")
            tmp_ct_partab=findstrnext(tmp_ct_partab,":")    #获取分区列
            if firstcol==tmp_ct_partab:
                audit_at.append("主键索引"+pkname+"的前导列"+firstcol+"涉及分区表的分区字段,不合理；")
                flag=1

        #索引列是否存在的判断（跟表的列进行对比）# print dict_ct_tab_col
        try:
            tmp_list_tabcols=dict_ct_tab_col[tabname]
        except:
            audit_at.append("在文本中，没有找到主键索引"+pkname+"所在的表"+tabname+"的正确建表语句；")
            flag=1
        else:
            tmp_list_tabcols=dict_ct_tab_col[tabname]  #表的全部列 tmp_list_tabcols
            #全部索引列tmp_list
            re=comparetwolists(tmp_list_tabcols,tmp_list)
            if re[1]!=[]: #tmp_list 有多余的值 就是索引列不存在
                noexistscol=','.join(re[1])
                seqerr=[]
                seqerr.append("错误:主键索引列"+noexistscol+"不存在,请检查创建表"+tabname+"的语句中是否存在该字段；")
                dictoutput={'status':1,'type':'addpk','content':orig_sql_str,'results':seqerr}
                return dictoutput

        #print tabname     #表名处理完毕
        #print pkname     #主键索引名处理完毕
        #print new_m       #主键索引列处理完毕 字符串 各列用,分隔


        #判断主键名相关       
        if pkname.startswith(dict_config['pkname_config']):
            pass
        else:
            audit_at.append("主键名"+str(pkname)+"不符合规范,请以"+dict_config['pkname_config']+"开头；")
            flag=1

        if namecheck(pkname):
            audit_at.append("错误：主键名"+str(pkname)+namecheck(pkname)+"；")
            flag=1

        b=new_m.count(",")+1             #获取主键列的个数
        if b>int(dict_config['pk_max_colnum']):
            audit_at.append("主键"+pkname+"联合列数量大于"+str(dict_config['pk_max_colnum'])+",顺序:"+new_m+",请注意；")
            flag=1

        if ct_part_tabnames.count(tabname)>0: #看这个表是分区表
            if not findanystr(sql_str,'LOCAL'):
                audit_at.append("分区表上请不要使用全局主键索引"+pkname+",请添加local关键字；")
                flag=1


    #表空间
    if findanystr(sql_str,'TABLESPACE'):
        tabspacename=findstrnext(sql_str,'TABLESPACE')
        if tabspacename==0:
            audit_at.append("表空间为空，该模块应使用 %s 表空间；" %dict_config['ind_tbs'])
            flag=1
        elif tabspacename!=dict_config['ind_tbs']:
            audit_at.append("表空间不准确，该模块应使用 %s 表空间；" %dict_config['ind_tbs'])
            flag=1
    else:
        audit_at.append("没有指定主键索引表空间, 该模块使用 %s 表空间；" %dict_config['ind_tbs'])
        flag=1


    #重复创建主键处理
    tabpkname = tabname+"."+pkname
    if tabpkname in at_pknames:
        audit_at.append("错误：主键 %s 已存在；"%tabpkname)
    else:
        at_pknames.append(tabpkname)
        at_pktabnames.append(tabname)
        dict_at_pk_col[tabname+"."+pkname]=new_m #非常重要
        #print dict_at_pk_col
        #print at_pknames
        #print at_pktabnames
        
        
    if flag==1:
        dictoutput={'status':1,'type':'addpk','content':orig_sql_str,'results':audit_at}
    else:
        audit_at=["符合规范，审核通过；"]
        dictoutput={'status':0,'type':'addpk','content':orig_sql_str,'results':audit_at}
    return dictoutput


def addcol(sql_str):
    dictoutput={}
    dict_addcol_tab_col_tmp={}
    audit_addcol=[]
    list_col=[]
    list_datatype=[]
    flag=0
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    if sql_str.find('ADD('):
        sql_str=sql_str.replace("ADD(","ADD (")
    addcol_tab=findstrnext(sql_str,'TABLE')
    addcol_info=findstrnext(sql_str,'ADD')
    #print addcol_info
    if addcol_tab==0 or addcol_info==0 or (addcol_tab=='ADD'):
        seqerr=[]
        seqerr.append("错误：语法出错；")
        dictoutput={'status':2,'type':'addcol','content':orig_sql_str,'results':seqerr}
        return dictoutput

    #处理表名
    addcol_tab = namesplit(addcol_tab)#获取表名

        
    #添加多列的情况有（）
    if addcol_info.startswith('('):  
        a=find_cont_firstparenthesis(sql_str)
        if a[0]==1:
            seqerr=[]
            seqerr.append("错误：语法出错；")
            dictoutput={'status':2,'type':'addcol','content':orig_sql_str,'results':seqerr}
            return dictoutput
        mx=remove_cont_parenthesis(a[3])#删除字符串中所有括号和括号里面的内容

        #继续处理获取列名和所有字段类型 需要把not null default x等关键字去掉
        mx_tmpstr=mx.replace(","," ") #将逗号替换成空格
        mx_tmpstr=removespaces(mx_tmpstr)  #删除字符串中多余的空格
        list_mx=mx_tmpstr.split(' ')  #转为列表
        list_mx2=removetheoneafter(list_mx,'DEFAULT') #删除default后面的元素
        listfinal=removesomeitems(list_mx2,['NOT','NULL','DEFAULT']) #删除NOT NULL DEFAULT元素
        #print listfinal
        
        tmpnum=0
        for i in listfinal:
            if tmpnum%2==1:
                list_datatype.append(i)
            else:
                list_col.append(i)
            tmpnum=tmpnum+1

      
        #print list_col  #输出所有列名 
        #print list_datatype # 输出所有字段类型 列表形式
            
        #处理重复列名
        dict_tmp_ct_cols=analyseRepeat(list_col)
        for item in dict_tmp_ct_cols:
            if dict_tmp_ct_cols[item]>1:
                audit_addcol.append("错误：表"+addcol_tab+"重复创建列"+str(item)+" "+str(dict_tmp_ct_cols[item])+"次；")
                flag=1
                list_col=delRepeat(list_col)


        #判断字段类型    
        wrongcoltype = removesomeitems(list_datatype,dict_config['coltype_standard']) #配置项 去除合规的字段类型
        wrongcoltype=delRepeat(wrongcoltype)
        str_wrongcoltype=' '.join(wrongcoltype)
        #print str_wrongcoltype
        if wrongcoltype != []:
            audit_addcol.append("使用了"+str_wrongcoltype+"类型的字段,请尽量使用varchar2、char,number,date四种字段类型；")
            flag=1

        noexistscoltype=removesomeitems(list_datatype,dict_config['coltype_total']) #配置项
        if noexistscoltype!=[]:
            audit_addcol.append(' '.join(noexistscoltype)+"可能是无效的字段类型；")
            flag=1


        #结果记录 记录列名和表名
        if dict_ct_tab_col.has_key(addcol_tab):
            for key in list_col:
                if key in dict_ct_tab_col[addcol_tab]:
                    audit_addcol.append("错误：表 %s 中已存在列名为 %s 的列；"%(addcol_tab,key))
                    flag = 1
                else:
                    dict_ct_tab_col[addcol_tab].append(key)
        else:
            dict_ct_tab_col[addcol_tab]=list_col

        #print dict_ct_tab_col


        if flag==1:
            dictoutput={'status':1,'type':'addcol','content':orig_sql_str,'results':audit_addcol}
        else:
            audit_addcol=["符合规范，审核通过；"]
            dictoutput={'status':0,'type':'addcol','content':orig_sql_str,'results':audit_addcol}
        return dictoutput

    

    #添加单列的情况
    else:
        #列类型处理
        addcol_coltype=findstrnext(sql_str,addcol_info)
        if addcol_coltype==0:
            seqerr=[]
            eqerr.append("错误:语法出错；")
            dictoutput={'status':2,'type':'addcol','content':orig_sql_str,'results':seqerr}
            return dictoutput

        addcol_coltype=remove_cont_parenthesis(addcol_coltype) #去掉括号和其内容
        #print addcol_coltype
            
        if  addcol_coltype not in dict_config['coltype_standard']:
            audit_addcol.append("使用了"+addcol_coltype+"类型的字段,请尽量使用varchar2、char,number,date四种字段类型；")
            flag=1                
        if  addcol_coltype not in dict_config['coltype_total']:
            audit_addcol.append("可能使用了无效的字段类型；")
            flag=1


        if findanystr(sql_str,'DEFAULT'):
            if findstrnext(sql_str,'DEFAULT')==0:
                seqerr=[]
                seqerr.append("错误：语法出错；")
                dictoutput={'status':2,'type':'addcol','content':orig_sql_str,'results':seqerr}
                return dictoutput
            elif findstrnext(sql_str,'DEFAULT')!=0:
                if  not findallstr(sql_str,'NOT NULL'):
                    audit_addcol.append("有默认值的情况下请添加NOT NULL否则造成长时间锁表；")
                    flag=1

                tmp=findstrnext(sql_str,'DEFAULT')
                if tmp.find("''")!=-1  or tmp.find('""')!=-1:
                    flag=1
                    audit_addcol.append("默认值为空；")
        if not findanystr(sql_str,'DEFAULT') and findallstr(sql_str,'NOT NULL'):
            audit_addcol.append("对已有表新增列不可为空且无默认值；")
            flag=1

        #结果记录 记录列名和表名
        #addcol_tab
        #addcol_info
        if dict_ct_tab_col.has_key(addcol_tab):
            if addcol_info in dict_ct_tab_col[addcol_tab]:
                audit_addcol.append("错误：表 %s 中已存在列名为 %s 的列；"%(addcol_tab,addcol_info))
                flag = 1
            else:
                dict_ct_tab_col[addcol_tab].append(addcol_info)

        else:
            dict_ct_tab_col[addcol_tab]=[]
            dict_ct_tab_col[addcol_tab].append(addcol_info)
            #ct_tabnames.append(addcol_tab) 这个暂时不记录

        #print ct_tabnames
        #print dict_ct_tab_col

        if flag==1:
            dictoutput={'status':1,'type':'addcol','content':orig_sql_str,'results':audit_addcol}
        else:
            audit_addcol=["符合规范，审核通过"]
            dictoutput={'status':0,'type':'addcol','content':orig_sql_str,'results':audit_addcol}
        return dictoutput






def adduk(sql_str):
    dictoutput={}
    audit_atuk=[]
    flag=0
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    ukname=findstrbefore(sql_str,'UNIQUE') #抽取唯一约束的约束名
    tabname=findstrnext(sql_str,'TABLE')    #抽取表名
    a=find_cont_firstparenthesis(sql_str)   #利用函数 获取第一个括号中的信息
    n=a[0]                               #获取标志位
    m=a[3]                               #获取第一个括号中的信息
    #print m
    tmpm=m.replace(","," ") #将逗号替换掉
    tmpm=removespaces(tmpm)  #删除字符串中多余的空格
    li_tmpm=tmpm.split(' ')    #转为列表
    m=','.join(li_tmpm) #获取列信息 转为字符串
    #print m

    if ukname==0 or tabname==0 or n==1:
        seqerr=[]
        seqerr.append("语法错误；")
        dictoutput={'status':2,'type':'adduk','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        tabname = namesplit(tabname)#获取表名
        #print tabname
        ukname = namesplit(ukname)#获取约束名
        #print ukname
        
        #一个唯一约束的列名重复 那么会报错
        tmp_list=m.split(",")
        dict_tmp_ci_cols=analyseRepeat(tmp_list)
        for key2 in dict_tmp_ci_cols:
            if dict_tmp_ci_cols[key2]>1:
                audit_at.append("唯一约束"+ukname+"重复出现列"+key2+""+str(dict_tmp_ci_cols[key2])+"次；")
                flag=1
        #删除重复的列名
        tmp_list=delRepeat(tmp_list)
        new_m=','.join(tmp_list)
        #print new_m
    
        #索引前导列判断
        firstcol=tmp_list[0]  #前导列

        if findanystr(firstcol,'TIME')==1 or findanystr(firstcol,'DATE')==1: #判断是否时间字段
            audit_atuk.append("唯一约束"+ukname+"的前导列"+firstcol+"涉及时间字段,不合理；")
            flag=1

        #判断是否分区字段
        try:
            tmp_ct_partab=dict_ct_partab[tabname]
        except:
            pass
        else:
            tmp_ct_partab=dict_ct_partab[tabname]
            tmp_ct_partab=tmp_ct_partab.replace(":",": ")
            tmp_ct_partab=findstrnext(tmp_ct_partab,":")    #获取分区列
            if firstcol==tmp_ct_partab:
                audit_atuk.append("唯一约束"+ukname+"的前导列"+firstcol+"涉及分区表的分区字段,不合理；")
                flag=1

        #索引列是否存在的判断（跟表的列进行对比）# print dict_ct_tab_col
        try:
            tmp_list_tabcols=dict_ct_tab_col[tabname]
        except:
            audit_atuk.append("在文本中，没有找到唯一约束"+ukname+"所在的表"+tabname+"的正确建表语句；")
            flag=1
        else:
            tmp_list_tabcols=dict_ct_tab_col[tabname]  #表的全部列 tmp_list_tabcols
            #全部索引列tmp_list
            re=comparetwolists(tmp_list_tabcols,tmp_list)
            if re[1]!=[]: #tmp_list 有多余的值 就是索引列不存在
                noexistscol=','.join(re[1])
                seqerr=[]
                seqerr.append("错误：唯一约束的列"+noexistscol+"不存在,请检查创建表"+tabname+"的语句中是否存在该字段；")
                dictoutput={'status':1,'type':'adduk','content':orig_sql_str,'results':seqerr}
                return dictoutput


        #print tabname     #表名处理完毕
        #print ukname     #唯一索引名处理完毕
        #print new_m       #唯一索引列处理完毕 字符串 各列用,分隔


        #判断约束名相关       
        if ukname.startswith(dict_config['ukname_config']):
            pass
        else:
            audit_atuk.append("约束名"+str(ukname)+"不符合规范,请以"+dict_config['ukname_config']+"开头；")
            flag=1

        if namecheck(ukname):
            audit_atuk.append("错误：约束名"+str(ukname)+namecheck(ukname)+"；")
            flag=1
 

        b=new_m.count(",")+1             #获取唯一索引列的个数
        if b>=int(dict_config['uk_max_colnum']):
            audit_atuk.append("唯一约束"+ukname+"联合列数量大于等于"+str(dict_config['uk_max_colnum'])+",顺序:"+new_m+",请注意；")
            flag=1

        if ct_part_tabnames.count(tabname)>0: #看这个表是分区表
            if not findanystr(sql_str,'LOCAL'):
                audit_atuk.append("分区表上请不要使用全局唯一索引"+ukname+",请添加local关键字；")
                flag=1


    #表空间
    if findanystr(sql_str,'TABLESPACE'):
        tabspacename=findstrnext(sql_str,'TABLESPACE')
        if tabspacename==0:
            audit_atuk.append("表空间为空，该模块应使用 %s 表空间；" %dict_config['ind_tbs'])
            flag=1
        elif tabspacename!=dict_config['ind_tbs']:
            audit_atuk.append("表空间不准确，该模块应使用 %s 表空间；" %dict_config['ind_tbs'])
            flag=1
    else:
        audit_atuk.append("没有指定唯一约束的索引表空间, 该模块使用 %s 表空间；" %dict_config['ind_tbs'])
        flag=1


    #重复创建唯一约束处理
    tabukname = tabname+"."+ukname
    if tabukname in at_uknames:
        audit_atuk.append("错误：唯一约束 %s 已存在；"%tabukname)
    else:
        at_uknames.append(tabukname)
        dict_at_uk_col[tabname+"."+ukname]=new_m #非常重要

        #print at_uknames      #记录创建唯一约束语句中的约束名（表名.约束名） 
        #print dict_at_uk_col  #记录创建唯一约束语句中的约束名和对应的列 （表名.约束名：col1,col2)
        
        
    if flag==1:
        dictoutput={'status':1,'type':'adduk','content':orig_sql_str,'results':audit_atuk}
    else:
        audit_atuk=["符合规范，审核通过；"]
        dictoutput={'status':0,'type':'adduk','content':orig_sql_str,'results':audit_atuk}
    return dictoutput

                

def renamecol(sql_str):
    flag=0
    dictoutput={}
    audit_renamecol=[]
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    renamecol_tab=findstrnext(sql_str,'TABLE')
    renamecol_col=findstrnext(sql_str,'COLUMN')
    renamecol_col2=findstrnext(sql_str,'TO')

    if renamecol_tab==0 or renamecol_col==0 or renamecol_col2==0:
        seqerr=[]
        seqerr.append("错误：语法出错；")
        dictoutput={'status':2,'type':'renamecol','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        renamecol_tab = namesplit(renamecol_tab)#获取表名


        if dict_ct_tab_col.has_key(renamecol_tab):
            if (renamecol_col in dict_ct_tab_col[renamecol_tab]) and (renamecol_col2 not in dict_ct_tab_col[renamecol_tab]):
                dict_ct_tab_col[renamecol_tab].remove(renamecol_col)
                dict_ct_tab_col[renamecol_tab].append(renamecol_col2)
            elif renamecol_col not in dict_ct_tab_col[renamecol_tab]:
                audit_renamecol.append("错误：表 %s 不存在列名为 %s 的列；"%(renamecol_tab,renamecol_col))
                flag=1
            elif renamecol_col2 in dict_ct_tab_col[renamecol_tab]:
                audit_renamecol.append("错误：表 %s 已存在列名为 %s 的列；"%(renamecol_tab,renamecol_col2))
                flag=1
        else:
            #dict_ct_tab_col[renamecol_tab]=[]
            #dict_ct_tab_col[renamecol_tab].append(renamecol_col2)
            pass

    #print dict_ct_tab_col

    if flag==1:
        dictoutput={'status':1,'type':'renamecol','content':orig_sql_str,'results':audit_renamecol}
        return dictoutput
    else:
        audit_renamecol=["符合规范，审核通过（生产系统中更改列名可能导致程序受影响）；"]
        dictoutput={'status':0,'type':'renamecol','content':orig_sql_str,'results':audit_renamecol}
        return dictoutput


def modifycol(sql_str):
    dictoutput={}
    dict_modifycol_tab_col_tmp={}
    audit_modifycol=[]
    flag=0
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    modifycol_tab=findstrnext(sql_str,'TABLE')
    modifycol_col=findstrnext(sql_str,'MODIFY')
    if modifycol_tab==0 or modifycol_col==0:
        seqerr=[]
        seqerr.append("错误：语法出错；")
        dictoutput={'status':2,'type':'modifycol','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        modifycol_tab = namesplit(modifycol_tab)#获取表名
        #print modifycol_tab
        #print modifycol_col

        if dict_ct_tab_col.has_key(modifycol_tab):
            if modifycol_col not in dict_ct_tab_col[modifycol_tab]:
                audit_modifycol.append("错误：表 %s 不存在列名为 %s 的列；"%(modifycol_tab,modifycol_col))
                flag=1
    if flag==1:
        dictoutput={'status':1,'type':'modifycol','content':orig_sql_str,'results':audit_modifycol}
        return dictoutput
    else:
        audit_modifycol=["符合规范，审核通过（注意不要进行缩小字段长度的操作）；"]
        dictoutput={'status':0,'type':'modifycol','content':orig_sql_str,'results':audit_modifycol}
        return dictoutput


def dropcol(sql_str):
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    dictoutput={}
    dict_dropcol_tab_col_tmp={}
    audit_dropcol=[]
    dropcol_tab=findstrnext(sql_str,'TABLE')
    dropcol_col=findstrnext(sql_str,'COLUMN')

    if dropcol_tab==0 or dropcol_col==0:
        seqerr=[]
        seqerr.append("错误：语法出错；")
        dictoutput={'status':2,'type':'dropcol','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        dropcol_tab = namesplit(dropcol_tab)#获取表名
        #print dropcol_tab
        #print dropcol_col
        if dict_ct_tab_col.has_key(dropcol_tab):
            if dropcol_col in dict_ct_tab_col[dropcol_tab]:
                dict_ct_tab_col[dropcol_tab].remove(dropcol_col)
            else:
                audit_dropcol.append("表 %s 不存在列名为 %s 的列；"%(dropcol_tab,dropcol_col))

    audit_dropcol.append("删除列会造成长时间锁表，请与DBA沟通；")
    dictoutput={'status':1,'type':'dropcol','content':orig_sql_str,'results':audit_dropcol}
    return dictoutput


def dropconst(sql_str):
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    dictoutput={}
    dict_dropconst_tab_col_tmp={}
    audit_dropconst=[]
    dropconst_tab=findstrnext(sql_str,'TABLE')
    dropconst_const=findstrnext(sql_str,'CONSTRAINT')

    if dropconst_tab==0 or dropconst_const==0:
        seqerr=[]
        seqerr.append("错误：语法出错；")
        dictoutput={'status':2,'type':'dropconst','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        dropconst_tab = namesplit(dropconst_tab)#获取表名
        #print dropconst_tab
        #print dropconst_const

    audit_dropconst.append("删除约束会导致对应索引消失和带来业务风险,请与DBA沟通；")
    dictoutput={'status':1,'type':'dropconst','content':orig_sql_str,'results':audit_dropconst}
    return dictoutput





def droptab(sql_str):
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    dictoutput={}
    audit_droptab=[]
    droptab_name=findstrnext(sql_str,'TABLE')

    if droptab_name==0:
        seqerr=[]
        seqerr.append("错误：语法出错；")
        dictoutput={'status':2,'type':'droptab','content':sql_str,'results':seqerr}
        return dictoutput
    else:
        droptab_name = namesplit(droptab_name)#获取表名
        #print droptab_name
        #if not dict_ct_tab_col.has_key(droptab_name):
        #    audit_droptab.append("此文件中不存在表 %s ，请检查表名是否正确"%droptab_name)

    audit_droptab.append("不允许删除表操作，请与DBA沟通；")
    dictoutput={'status':1,'type':'droptab','content':sql_str,'results':audit_droptab}
    return dictoutput


def dropseq(sql_str):
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    dictoutput={}
    audit_dropseq=[]
    dropseq_name=findstrnext(sql_str,'SEQUENCE')

    if dropseq_name==0:
        seqerr=[]
        seqerr.append("错误：语法出错；")
        dictoutput={'status':2,'type':'dropseq','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        #处理序列名
        dropseq_name = namesplit(dropseq_name)
            
    audit_dropseq.append("不允许删除序列操作，请与DBA沟通；")
    dictoutput={'status':1,'type':'dropseq','content':orig_sql_str,'results':audit_dropseq}
    return dictoutput

def dropidx(sql_str):
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    dictoutput={}
    audit_dropind=[]
    dropind_name=findstrnext(sql_str,'INDEX')

    if dropind_name==0:
        seqerr=[]
        seqerr.append("错误：语法出错；")
        dictoutput={'status':2,'type':'dropidx','content':orig_sql_str,'results':seqerr}
        return dictoutput
    else:
        #处理索引名
        dropind_name = namesplit(dropind_name)

    audit_dropind.append("不允许删除索引操作，请与DBA沟通；")
    dictoutput={'status':1,'type':'dropidx','content':orig_sql_str,'results':audit_dropind}
    return dictoutput



  #####################
#Part4 汇总审核功能函数#
  #####################
  
#汇总类审核函数
def summary():
    list_return=[]
    funcnamelist=['summary_sqltype','summary_idx','summary_commenttab','summary_commentcol','summary_pk','summary_parttab']
    for funcname in funcnamelist:
        dict_re = eval(funcname)()
        if dict_re:
            list_return.append(dict_re)
        else:
            continue
    return list_return



def summary_sqltype():
    dictoutput={}
    audit_text=[]
    totalddl=0
    for key in sqltype_count:
        if sqltype_count[key]!=0:
            totalddl+=sqltype_count[key]
            audit_text.append(str(key)+":"+str(sqltype_count[key]))
        else:
            pass
    if totalddl!=0:
        audit_text.insert(0,"《搜索到"+str(totalddl)+"句DDL》")#在头部插入
    if audit_text!=[]:
        dictoutput={'status':0,'type':'N/A','content':"语句统计",'results':audit_text}

    return dictoutput


def summary_idx():
    dictoutput = {}
    audit_ci_summary=[]
    reden_flag=0
    tabind = {} #记录表的全部索引名 {T1:[I1_1,I1_2,I1_3],T2:[I2_1,I2_2]}
    #print ci_indnames  # 列表 表名.索引名
    #print at_uknames   # 列表 表名.唯一约束名
    all_indnames=ci_indnames+at_uknames
    all_indnames=delRepeat(all_indnames)
    #print all_indnames
    for val in all_indnames:
        tabname,indname=val.split('.')
        #print tabname
        #print indname
        if tabind.has_key(tabname):
            tabind[tabname].append(indname)
        else:
            tabind[tabname]=[indname]

    #统计一个表上的索引总个数超过2个的并输出 并将有2个索引或以上的表名收集
    #print tabind
    for key in tabind:
        indnum = len(tabind[key])
        if indnum>int(dict_config['max_indnum_eachtable']): #配置项
            audit_ci_summary.append("表"+key+"上面有"+str(indnum)+"个索引,大于"+str(dict_config['max_indnum_eachtable'])+"个请注意；")

                        
    #冗余的索引处理#
    list_tmp_indcols=[]
    list_indcols=[]
    dict_all_ind_col=mergedict(dict_ci_ind_col,dict_at_uk_col)
    #print dict_all_ind_col        
    for tabname in tabind:
        for indname in tabind[tabname]:
            tabindname=tabname+"."+indname
            list_indcols.append(dict_all_ind_col[tabindname])

        #print tabname
        #print list_indcols
        
        for item in list_indcols:
            list_indcols_tmp=copy.deepcopy(list_indcols)
            list_indcols_tmp.remove(item)
            #print item
            #print list_indcols_tmp
            for key in list_indcols_tmp:
                if key.startswith(item):
                    reden_flag=1

    if reden_flag==1:
        audit_ci_summary.append("表"+tabname+"上面有冗余索引,请合理设计；")
                       
    if audit_ci_summary!=[]:
        dictoutput={'status':1,'type':'N/A','content':"索引汇总",'results':audit_ci_summary}

    return dictoutput



def summary_commenttab():
    dictoutput = {}
    audit_co_summary = []
    for tabname in ct_tabnames:
        if tabname not in comtab_tabnames:
            audit_co_summary.append("表 %s 没有表级注释语句,请添加；"%tabname)
    if audit_co_summary!=[]:
        dictoutput={'status':1,'type':'N/A','content':"表注释汇总",'results':audit_co_summary}
    return dictoutput


def summary_commentcol():
    #print dict_comcol_tab_col #记录列注释语句的表和表的列 {'T1': ['COL1', 'COL2']}
    audit_col_summary = []
    dictoutput = {}
    for tabname in dict_ct_tab_col:
        if dict_comcol_tab_col.has_key(tabname):
            cl_collist=dict_ct_tab_col[tabname]
            co_collist=dict_comcol_tab_col[tabname]
            #求差集
            lostcollist = list(set(cl_collist).difference(set(co_collist)))
            if lostcollist!=[]:
                lostcolstr = ','.join(lostcollist)
                audit_col_summary.append("表 %s 少了注释列 %s；"%(tabname,lostcolstr))
        else:
            audit_col_summary.append("表 %s 没有任何列注释语句,请添加；"%tabname)
            

    if audit_col_summary!=[]:
        dictoutput={'status':1,'type':'N/A','content':"列注释汇总",'results':audit_col_summary}
    return dictoutput


def summary_pk():
    #建主键语句审核汇总
    audit_at_summary=[]
    dictoutput={}

    #表建议都要有主键
    lostpktab = set(ct_tabnames).difference(set(at_pktabnames))
    if len(lostpktab)>0:
        for tabname in lostpktab:
            audit_at_summary.append("表 %s 没有主键，表必须要有主键，请添加；"%tabname)

    if audit_at_summary!=[]:
        dictoutput={'status':1,'type':'N/A','content':"主键情况汇总",'results':audit_at_summary}

    return dictoutput


def summary_parttab():
    audit_part = []
    dictoutput={}
    ct_nopart_tabnames=removesomeitems(ct_tabnames,ct_part_tabnames)
    #print ct_nopart_tabnames
    #分区建议  比如表名涉及ORDER LOG等关键字 但没有分区
    for item in ct_nopart_tabnames:
        if item.find("LOG")==-1 and  item.find("ORDER")==-1:
            pass
        else:
            audit_part.append("建议将日志表或订单表"+item+"进行分区；")
    if audit_part!=[]:
        dictoutput = {'status':1,'type':'N/A','content':"分区表情况汇总",'results':audit_part}
    return dictoutput


        




                



