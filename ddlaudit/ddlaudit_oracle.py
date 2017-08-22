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
from str_manipulation import bracklet_split #对字符串以,分隔为列表，可避免k1,k2(k3,k4),k5这种情况的分割异常 [k1,k2(k3,k4),k5] 
from str_manipulation import remove_comma_childstr#对字符串以,分隔为列表,如果列表元素中有相关关键字那么删除这个元素 返回字符串
from str_manipulation import namesplit     #将字符串owner.object_name 以.分隔并返回object_name  
from str_manipulation import namecheck     #检查对象名长度不超过30并不能用数字开头

from list_manipulation import delRepeat    #删除列表中的重复项  相同项只保留一个
from list_manipulation import analyseRepeat #统计列表中的重复项 返回一个字典
from list_manipulation import comparetwolists   #对比两个列表,将差异返回为一个元祖（两个列表） 输入的列表不要有重复项
from list_manipulation import removesomeitems #删除列表中的一些项，删除项来自列表remove_list  符合这些项的全部删除
from list_manipulation import removetheoneafter #删除列表中某个项的后面一项

from dict_manipulation import mergedict #将两个字典的内容合并

from dealsqltext import dealsqltext#处理待审核的sql文本格式 

from check_online_structure import CheckOnlineStructure

#非网页版测试使用
#from config import dict_config#导入审核规则配置项
#from output import make_txt #将审核结果记录到文本
#import chardet



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
    ci_indnames=[]         #记录表名.索引名 
    global ci_inds
    ci_inds=[]         #记录索引名 
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

    global at_pknames            #记录 表名.主键名
    at_pknames=[]                
    global at_pks                #记录主键名 
    at_pks=[]
    global at_pktabnames
    at_pktabnames=[]             #记录创建主键语句中的表名
    global dict_at_pk_col
    dict_at_pk_col={}            #记录创建主键语句中的主键名和对应的列 (表名.主键名:col1,col2)

    global at_uknames             #记录表名.约束名
    at_uknames=[]      
    global at_uks                #记录约束名 
    at_uks=[]
    global dict_at_uk_col
    dict_at_uk_col={}  #记录创建唯一约束语句中的约束名和对应的列 （表名.约束名：col1,col2)

    #sql语句类型统计 共计18种
    global sqltype_count
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

    #让CREATE TABLE在CREATE.*INDEX之前判断 不然create table中有index关键字会有问题 
    #(^CREATE TABLE.*AS SELECT.*)在(^CREATE TABLE.*)之前
    tuple_tmp=("(^CREATE TABLE.*AS SELECT.*)","(^CREATE TABLE.*)","(^CREATE.*INDEX.*)","(^CREATE SEQUENCE.*)",
        "(^COMMENT ON TABLE.*)","(^COMMENT ON COLUMN.*)","(^TRUNCATE.*)","(^ALTER TABLE.*)","(^DROP.*)")
    for key in tuple_tmp:
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
    altertab_filter = {"(^ALTER TABLE.*ADD.*PRIMARY KEY.*)":"addpk",#CONSTRAINT不要了
                  "(^ALTER TABLE.*ADD CONSTRAINT.*UNIQUE.*)":"adduk",
                 "(^ALTER TABLE.*ADD.*)":"addcol",
                 "(^ALTER TABLE.*RENAME COLUMN.*)":"renamecol",
                 "(^ALTER TABLE.*MODIFY.*)":"modifycol",
                 "(^ALTER TABLE.*DROP COLUMN.*)":"dropcol",
                 "(^ALTER TABLE.*DROP CONSTRAINT.*)":"dropconst"
                 }
    for key in altertab_filter:
        #print key
        res=search(key,alter_str,re.DOTALL|re.IGNORECASE)  #正则处理
        if res:
            return altertab_filter[key]
        else:
            continue
    return "othersql" 


#审核sql主功能函数
def process_sqlfile(sqltext,dict_config_input,privilege_flag_input,*args):
    global dict_config
    dict_config=dict_config_input
    init_variable() 
    list_auditresult=[]
    fsqlfinal = dealsqltext(sqltext)

    #结合线上结构进行审核
    global online_info_flag
    try:
        username,password,ip,port,servicename=args
        #print "username",username,"password",password,"ip",ip,"port",port,"servicename",servicename
        global checkobj
        checkobj=CheckOnlineStructure(username,password,ip,port,servicename)
    except:
        online_info_flag=1#无法进行线上验证
    else:
        online_info_flag=0 #可以进行线上验证
    #print "online_info_flag",online_info_flag

    

    
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
    for item in list_auditsummary:
        if item['type']=='summary_sqltype':
            list_auditresult.insert(0,item)
        else:
            list_auditresult.append(item)

    #是否权限分离
    if privilege_flag_input=='y':
        list_auditresult.append(
            {'type':'summary_grant','content':"授权提示",
             'results':[(3,'相关对象可能需要对_APP等用户进行授权,利用平台生成授权脚本')]}
             )


    
    #列注释语句太多 不再单句输出 合并在一起后输出
    #{'type':'commentcol','content':orig_sql_str,'results':audit_col}
    list_return=[]
    list_tmp_ok=[]
    for item in list_auditresult:
        if item['type']=="commentcol":
            okflag=0
            for subitem in  item['results']:
                if subitem[0]!=0:#通过 info 警告 warning #错误  wrong
                    okflag=1
            if okflag==1:
                list_return.append(item)
            else:
                list_tmp_ok.append(item['content'])
        else:
            list_return.append(item)
    
    if list_tmp_ok!=[]:
        list_return.append({'type':'comcol_gather','content':'\n'.join(list_tmp_ok),'results':[(0,"符合规范,审核通过")]})


    #返回
    return list_return




  #####################
#Part3 审核功能函数#
  #####################




def createtab_select(sql_str):
    audit_ctas = []

    #利用正则表达式去除处于TABLE和AS之间的表名
    tmp_str = re.search("(?<=TABLE) .* (?=AS)",sql_str,re.DOTALL|re.IGNORECASE)
    if tmp_str==None:
        return {'type':'createtab_select','content':sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        ct_tabname = tmp_str.group().strip()
        ct_tabname = namesplit(ct_tabname).upper()
        #print ct_tabname


    #重复创建表处理
    if ct_tabname in ct_tabnames:
        return {'type':'createtab_select','content':sql_str,'results':[(2,"错误：表"+ct_tabname+"在文本中重复创建")]}
    else:
        ct_tabnames.append(ct_tabname)

    #判断表名相关
    if namecheck(ct_tabname):
        audit_ctas.append((2,"错误：表名"+ct_tabname+namecheck(ct_tabname)))

    if online_info_flag==0:
        if checkobj.check_objname(ct_tabname,"TABLE")==0:
            audit_ctas.append((2,"错误：表"+ct_tabname+"线上已存在"))

    if not ct_tabname.startswith(dict_config['tabname_config']):#配置项
        audit_ctas.append((1,"表名"+ct_tabname+"不符合规范,请以"+dict_config['tabname_config']+"开头"))
    
    audit_ctas.append((1,"CTAS语句会使得新表丢失原表的default值属性，需注意"))
    #输出结果
    return {'type':'createtab_select','content':sql_str,'results':audit_ctas}




def createtab(sql_str):
    audit_ct=[]   #[(1,"blabla"),(2,"wronginfo")]
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    ct_tabname=findstrnext(sql_str,'TABLE')#抽取表名 
    a=find_cont_firstparenthesis(sql_str)#利用函数 获取第一个括号中的信息 
    n=a[0]                               #获取标志位
    m=a[3]                               #获取实际的内容  ID NUMBER,COL2 VARCHAR2(20),COL3 VARCHAR2(30) not null,COL4 VARCHAR2(30),constraint CODE primary key (id)
    if ct_tabname==0 or n==1:
        return {'type':'createtab','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        ct_tabname = namesplit(ct_tabname)#获取表名
        #print ct_tabname

        #重复创建表处理
        if ct_tabname in ct_tabnames:
            return {'type':'createtab','content':orig_sql_str,'results':[(2,"错误：表"+ct_tabname+"在文本中重复创建")]}
        else:
            ct_tabnames.append(ct_tabname)#记录表名

            #判断表名相关
            if not ct_tabname.startswith(dict_config['tabname_config']):#配置项
                audit_ct.append((1,"表名"+ct_tabname+"不符合规范,请以"+dict_config['tabname_config']+"开头"))

            if namecheck(ct_tabname):
                audit_ct.append((2,"错误：表名"+ct_tabname+namecheck(ct_tabname)))

            if online_info_flag==0:
                if checkobj.check_objname(ct_tabname,"TABLE")==0:
                    audit_ct.append((2,"错误：表"+ct_tabname+"线上已存在"))
        
        #提取主键   出现这种格式typecode char(2),constraint CODE PRIMARY KEY (typecode) 或者typecode char(2),PRIMARY KEY (typecode)
        #或 CONSTRAINT PK_PFS_LBS_MOBILE PRIMARY KEY (ID) USING INDEX TABLESPACE BPEP_FS_IDX_B01
        #都是不规范的要报错的

        t_list = bracklet_split(m)#以,为分隔符将字符串转为列表
        primary_key_item=""
        for item in t_list:
            if item.find('PRIMARY KEY')!=-1:
                primary_key_item = item
                break
        if primary_key_item!="":
            #primary_key_info=find_cont_firstparenthesis(primary_key_item)
            #primary_key_col=primary_key_info[3]#主键列信息
            audit_ct.append((1,"不要在建表语句中定义主键约束,需单独添加"))
            

        #提取列信息和字段类型
        #出现这种格式typecode char(2),constraint CODE PRIMARY KEY (typecode) 或者typecode char(2),PRIMARY KEY (typecode)
        #对字符串以,分隔为列表,如果列表元素中有PRIMARY KEY关键字那么删除这个元素 返回字符串   
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
    
        #print list_col  #输出所有列名 列表形式
        #print list_datatype # 输出所有字段类型 列表形式


        #处理重复列名
        dict_tmp_ct_cols=analyseRepeat(list_col)
        for key in dict_tmp_ct_cols:
            if dict_tmp_ct_cols[key]>1:
                audit_ct.append((2,"表"+ct_tabname+"重复创建列"+key+" "+str(dict_tmp_ct_cols[key])+"次"))

        #记录表的列信息
        dict_ct_tab_col[ct_tabname]=dict_tmp_ct_cols.keys()



        #判断字段类型    
        wrongcoltype = removesomeitems(list_datatype,dict_config['coltype_standard']) #配置项 去除合规的字段类型
        wrongcoltype=delRepeat(wrongcoltype)

        noexistscoltype=removesomeitems(list_datatype,dict_config['coltype_total']) #配置项
        tempmsg=""
        if wrongcoltype != []:
            tempmsg=tempmsg+"使用了"+'、'.join(wrongcoltype)+"字段类型,请尽量使用varchar2、char,number,date四种类型\n"
        if noexistscoltype!=[]:
            noexistscoltype=delRepeat(noexistscoltype)
            tempmsg=tempmsg+'、'.join(noexistscoltype)+"可能是无效的字段类型"

        if tempmsg!="":
            audit_ct.append((1,tempmsg))


        #判断5个要素字段 
        s1=set(dict_tmp_ct_cols.keys()) #所有列
        s2=set(dict_config['col_standard'])#标准列
        list_lack_col=list(s2-s1)#差集
        if list_lack_col!=[]:
            audit_ct.append((2,"缺少必须创建的字段："+'、'.join(list_lack_col) ))
        #判断字段名是否使用了保留关键字
        s3=set(dict_config['col_reserved'])
        list_wrongname_col=list(s1&s3)#交集
        if list_wrongname_col!=[]:
            audit_ct.append((2,"错误：字段"+'、'.join(list_wrongname_col)+"是ORACLE保留字段名"))


        
        #处理分区表的情况
        partition_type="" #分区类型
        y="" #分区字段
        if sql_str.find('PARTITION BY')!=-1:

            tmpline=sql_str[sql_str.find('PARTITION BY'):]
            partition_type=findstrnext(tmpline,'BY')#获取分区类型
            b=find_cont_firstparenthesis(tmpline)   #获取第一个括号中的信息
            x=b[0]                                  #获取标志位
            y=b[3]                                  #获取分区字段
            y=removespaces(y)
            if partition_type==0 or x==1:
                audit_ct.append((2,"错误：分区语法出错"))
            else:
                if partition_type not in ['HASH','LIST','RANGE']: #如果分区类型不是这三个那么报错
                    audit_ct.append((2,"错误：分区类型不存在"))
                if y.count(",")>0:                     #分区列只能是单列
                    audit_ct.append((2,"错误：分区键只能是单个字段"))
                if y not in list_col:               #分区列必须是建表中定义的列
                    audit_ct.append((2,"错误：分区键对应字段不存在"))
                #记录分区信息
                dict_ct_partab[ct_tabname]=partition_type+":"+y
                ct_part_tabnames.append(ct_tabname)       


    #表空间
    if findanystr(sql_str,'TABLESPACE'):
        tabspacename=findstrnext(sql_str,'TABLESPACE')
        if tabspacename==0:
            audit_ct.append((1,"表空间为空,该模块应使用 %s 表空间" %dict_config['data_tbs']))
        elif tabspacename!=dict_config['data_tbs']:
            #print tabspacename
            audit_ct.append((1,"表空间不准确,该模块应使用 %s 表空间" %dict_config['data_tbs']))
    else:
        audit_ct.append((1,"没有指定表空间,该模块使用 %s 表空间" %dict_config['data_tbs']))

    #输出结果
    #print ct_tabnames
    #print dict_ct_tab_col
    #print ct_part_tabnames
    #print dict_ct_partab
    if audit_ct!=[]:
        return {'type':'createtab','content':orig_sql_str,'results':audit_ct}
    else:
        return {'type':'createtab','content':orig_sql_str,'results':[(0,"符合规范,审核通过")]}



def createidx(sql_str):
    audit_ci=[]
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    idxname=findstrnext(sql_str,'INDEX') #抽取索引名
    tabname=findstrnext(sql_str,'ON')    #抽取表名  create index I_T1 on T1(COL1,COL2)  这里T1和（默认加了一个空格
    a=find_cont_firstparenthesis(sql_str)#利用函数 获取第一个括号中的信息
    n=a[0]                            #获取标志位
    m=a[3]                            #获取第一个括号中的信息
    m=removespaces(m)
    if idxname==0 or tabname==0 or n==1:
        return {'type':'createidx','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        tabname = namesplit(tabname)#获取表名
        idxname = namesplit(idxname)#获取索引名


        #分离索引字段,去除索引字段中的ASC DESC等约束条件
        ind_list=[]
        m=m.replace(","," ") #将逗号替换成空格
        m=removespaces(m)  #删除字符串中多余的空格
        #print m
        list_m=m.split(' ')  #转为列表
        ind_list=removesomeitems(list_m,['ASC','DESC']) #删除ASC DESC元素
        #检查索引列名重复
        dict_tmp_ci_cols=analyseRepeat(ind_list)
        for key in dict_tmp_ci_cols:
            if dict_tmp_ci_cols[key]>1:
                audit_ci.append((2,"错误：索引"+idxname+"重复出现"+key+"列"+str(dict_tmp_ci_cols[key])+"次"))
        ind_list=delRepeat(ind_list)        #删除重复的列名
        #print ind_list  索引列

        
        #记录索引信息
        tabindname = tabname+"."+idxname
        if tabindname in ci_indnames:
            return {'type':'createidx','content':orig_sql_str,'results':[(2,"错误：索引"+tabindname+"在文本中重复创建")]}
        else:
            ci_indnames.append(tabindname)
            dict_ci_ind_col[tabindname]=','.join(ind_list) #非常重要
        #print ci_indnames
        #print dict_ci_ind_col

        #重复建索引判断
        if idxname in ci_inds:
            return {'type':'createidx','content':orig_sql_str,'results':[(2,"错误：索引"+idxname+"在文本中重复创建")]}
        else:
            ci_inds.append(idxname)

        #判断索引名      
        if idxname.startswith(dict_config['indname_config']) or idxname.startswith(dict_config['uniqindname_config']):
            pass
        else:
            audit_ci.append((1,"索引名"+idxname+"不符合规范,请以"+dict_config['indname_config']+\
                             "或者"+dict_config['uniqindname_config']+"开头"))
        if namecheck(idxname):
            audit_ci.append((2,"错误：索引名"+idxname+namecheck(idxname)))



        #索引前导列判断
        firstcol=ind_list[0]  #前导列
        if findanystr(firstcol,'TIME')==1 or findanystr(firstcol,'DATE')==1: #判断是否时间字段
            audit_ci.append((1,"索引"+idxname+"的前导列"+firstcol+"涉及时间字段,容易发生问题"))


        #判断前导列是否分区字段
        #dict_ct_partab[ct_tabname]=partition_type+":"+y
        if dict_ct_partab.has_key(tabname):
            parkey=dict_ct_partab[tabname].split(":")[-1] #获取分区列
            if firstcol==parkey:
                audit_ci.append((1,"索引"+idxname+"的前导列"+firstcol+"涉及分区字段,设计不合理"))

        #索引列个数
        if len(ind_list) >dict_config['ind_max_colnum']:
            audit_ci.append((1,"索引"+idxname+"联合列数量大于"+str(dict_config['ind_max_colnum'])+",顺序:"+','.join(ind_list)))


        #索引对应的表是否在文本中创建 是的话判断列是否存在 
        # 不是的话从线上判断表和字段是否存在 索引名是否存在等
        if dict_ct_tab_col.has_key(tabname):
            tmp_list_tabcols=dict_ct_tab_col[tabname]  #获取表的列信息 
            list_noexistscol=list(set(ind_list)-set(tmp_list_tabcols))
            if list_noexistscol!=[]:
                audit_ci.append((2,"索引的列"+'、'.join(list_noexistscol)+"不存在,请检查文本中"+tabname+"建表语句的字段信息"))


        else:
            if online_info_flag==0:
                if checkobj.check_objname(tabname,"TABLE")==1:
                    audit_ci.append((2,"错误：线上不存在表"+tabname))
                else:
                    if checkobj.check_objname(idxname,"INDEX")==0:
                        audit_ci.append((2,"错误：线上已有同名索引"+idxname))

                    #相关字段是否有索引 这个比较复杂了 待完善

                    list_diff=checkobj.check_col(tabname,ind_list)
                    if isinstance(list_diff,list) and list_diff!=[]:
                        audit_ci.append((2,"错误：线上表结构中没有如下字段："+'、'.join(list_diff)))

                    if not findanystr(sql_str,'ONLINE'):
                        audit_ci.append((1,"为已有表创建索引,需添加online关键字在线创建"))

    #分区表的索引需要是local的
    if tabname in ct_part_tabnames:
        if not findanystr(sql_str,'LOCAL'):
            audit_ci.append((1,"分区表不能创建全局索引,请添加local关键字"))

    #表空间
    if findanystr(sql_str,'TABLESPACE'):
        tabspacename=findstrnext(sql_str,'TABLESPACE')
        if tabspacename==0:
            audit_ci.append((1,"表空间为空,该模块应使用 %s 表空间" %dict_config['ind_tbs']))
        elif tabspacename!=dict_config['ind_tbs']:
            audit_ci.append((1,"表空间不准确,该模块应使用 %s 表空间" %dict_config['ind_tbs']))
    else:
        audit_ci.append((1,"没有指定索引表空间,该模块使用 %s 表空间" %dict_config['ind_tbs']))

        
    #并行度
    if findanystr(sql_str,'PARALLEL'):
        audit_ci.append((1,"请不要打开并行创建索引"))


    #输出结果
    if audit_ci!=[]:
        return {'type':'createidx','content':orig_sql_str,'results':audit_ci}
    else:
        return {'type':'createidx','content':orig_sql_str,'results':[(0,"符合规范,审核通过")]}







def createseq(sql_str):
    audit_cs=[]
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    seqstr=findstrnext(sql_str,'SEQUENCE')
    if seqstr==0:
        return {'type':'createseq','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        seqname = namesplit(seqstr)#获取序列名

        #重复创建序列处理
        if seqname in cs_seqnames:
            return {'type':'createseq','content':orig_sql_str,'results':[(2,"错误：序列"+seqname+"在文本中重复创建")]}
        else:
            cs_seqnames.append(seqname)

        #线上结构验证
        if online_info_flag==0:
                if checkobj.check_objname(seqname,"SEQUENCE")==0:
                    audit_cs.append((2,"错误：线上已存在序列"+seqname))

        #审核序列名相关
        if not seqname.startswith(dict_config['seqname_config']): #配置项
            audit_cs.append((1,"序列名"+seqname+"不符合规范,请以"+dict_config['seqname_config']+"开头"))

        if namecheck(seqname):
            audit_cs.append((2,"错误：序列名"+seqname+namecheck(seqname)))

        #序列名可能有order关键字 需要排除
        if findanystr(sql_str.replace(seqname,''),'ORDER')==1 and findanystr(sql_str.replace(seqname,''),'NOORDER')==0:
            audit_cs.append((1,"请不要使用ORDER属性"))

        #审核参数相关
        if findstrnext(sql_str,'CACHE'):
            tmpstr=findstrnext(sql_str,'CACHE')
            try:
                num=int(tmpstr)
            except:
                audit_cs.append((2,"错误：序列的CACHE值指定不正确"))
            else:
                if num<int(dict_config['seqcache']): #配置项
                    audit_cs.append((1,"指定序列CACHE值小于阀值"+str(dict_config['seqcache'])))
        else:
            audit_cs.append((1,"序列没有指定CACHE值"))
        
        #循环序列
        if findanystr(sql_str,'CYCLE') and (not findanystr(sql_str,'NOCYCLE')):
            audit_cs.append((0,"循环序列,一般用于和时间信息拼接生成流水号等,注意长度"))
            if findstrnext(sql_str,'MAXVALUE'):
                tmpmaxvalue=findstrnext(sql_str,'MAXVALUE')
                try:
                    maxvalue=int(tmpmaxvalue)
                except:
                    audit_cs.append((2,"错误：循环序列MAXVALUE指定不正确"))
                else:
                    if len(str(maxvalue))<int(dict_config['seq_cycle_maxnum']): #配置项
                        audit_cs.append((1,"循环序列MAXVALUE位数小于"+str(dict_config['seq_cycle_maxnum'])))
            else:
                audit_cs.append((1,"循环序列没有指定MAXVALUE"))

        #输出结果
        if audit_cs!=[]:
            return {'type':'createseq','content':orig_sql_str,'results':audit_cs}
        else:
            return {'type':'createseq','content':orig_sql_str,'results':[(0,"符合规范,审核通过")]}

    
    


def commenttab(sql_str):
    audit_co=[]
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    co_tabname=findstrnext(sql_str,'TABLE') #抽取表名
    co_content=findstrnext(sql_str,'IS')  #抽取注释内容

    co_cont=sql_str.count("'")
    if co_cont==0:
        co_cont=sql_str.count('"')

    if co_tabname==0 or co_content==0 or co_cont%2!=0:
        return {'type':'commenttab','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}

    co_tabname = namesplit(co_tabname)#获取表名

    #重复表注释处理
    if co_tabname in comtab_tabnames:
        return {'type':'commenttab','content':orig_sql_str,'results':[(2,"错误：表"+co_tabname+"在文本中重复注释")]}
    else:
        comtab_tabnames.append(co_tabname)

    #注释为空
    if sql_str.find("''")!=-1  or sql_str.find('""')!=-1:
        audit_co.append((1,"注释内容为空"))

    
    #和建表语句进行对比 看是否有建表语句
    if co_tabname not in ct_tabnames:
        #判断线上结构
        if online_info_flag==0:
            if checkobj.check_objname(co_tabname,"TABLE")==1:
                audit_co.append((2,"错误：文本中无表"+co_tabname+"的创建语句、线上也没有该表"))
        
    #输出结果
    if audit_co!=[]:
        return {'type':'commenttab','content':orig_sql_str,'results':audit_co}
    else:
        return {'type':'commenttab','content':orig_sql_str,'results':[(0,"符合规范,审核通过")]}
        

def commentcol(sql_str):
    audit_col=[]
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    col_tabcol=findstrnext(sql_str,'COLUMN') #抽取表名和列名
    col_commenttabntent=findstrnext(sql_str,'IS')  #抽取注释内容

    col_commenttabnt=sql_str.count("'")
    if col_commenttabnt==0:
        col_commenttabnt=sql_str.count('"')

    if col_tabcol==0 or col_commenttabntent==0 or col_commenttabnt%2!=0:
        return {'type':'commentcol','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        if sql_str.find("''")!=-1  or sql_str.find('""')!=-1:
            audit_col.append((1,"注释内容为空"))
        
        #处理表名和列名
        list_tabcol=col_tabcol.split(".")
        col_tabname=list_tabcol[-2]
        col_col=list_tabcol[-1]
        #print col_tabname
        #print col_col

        #记录表
        if col_tabname not in comcol_tabnames:
            comcol_tabnames.append(col_tabname)
        #记录列
        if dict_comcol_tab_col.has_key(col_tabname):
            #重复列注释
            if col_col in dict_comcol_tab_col[col_tabname]:
                return {'type':'commentcol','content':orig_sql_str,'results':[(2,"错误：表"+col_tabname+"的列"+col_col+"在文本中重复注释")]}
            else:
                dict_comcol_tab_col[col_tabname].append(col_col)
        else:
            dict_comcol_tab_col[col_tabname]=[col_col]

        #print comcol_tabnames     
        #print dict_comcol_tab_col

        #和建表语句进行对比 看是否有建表语句 和对应的列
        #如果没有就去线上查询
        if col_tabname not in dict_ct_tab_col.keys():
            if online_info_flag==0:
                if checkobj.check_objname(col_tabname,"TABLE")==1:
                    audit_col.append((2,"错误：文本中无表"+col_tabname+"的创建语句、线上也没有该表"))
                else:
                    list_col=[]
                    list_col.append(col_col)
                    if  checkobj.check_col(col_tabname,list_col)==list_col:
                        audit_col.append((2,"错误：文本中无表"+col_tabname+"的创建语句、线上有该表但没有对应列"+col_col))

        else:
            if col_col not in dict_ct_tab_col[col_tabname]:
                audit_col.append((2,"错误：表"+col_tabname+"上不存在"+col_col+"字段"))

      
    #结果输出   
    if audit_col!=[]:
        return {'type':'commentcol','content':orig_sql_str,'results':audit_col}
    else:
        return {'type':'commentcol','content':orig_sql_str,'results':[(0,"符合规范,审核通过")]}
    
    

def truncate(sql_str):
    audit_truncate=[]
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    truncate_tab=findstrnext(sql_str,'TABLE')

    if truncate_tab==0:
        return {'type':'truncate','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        truncate_tab = namesplit(truncate_tab)#获取表名

        #print truncate_tab
        truncate_tabnames.append(truncate_tab)

        if online_info_flag==0:
            if checkobj.check_objname(truncate_tab,"TABLE")==1:
                audit_truncate.append((2,"错误：线上没有表"+truncate_tab))
            else:
                audit_truncate.append((1,"TRUNCATE操作执行后无法回退"))
        else:
            audit_truncate.append((1,"TRUNCATE操作执行后无法回退"))

        return {'type':'truncate','content':orig_sql_str,'results':audit_truncate}
        
        

def othersql(sql_str):
    return {'type':'othersql','content':sql_str,'results':[(1,"系统无法审核该语句类型")]}
    

def addpk(sql_str): 
    #alter table t1 add constraint PK_1 primary key(id) 
    audit_at=[]
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    pkname=findstrbefore(sql_str,'PRIMARY') #抽取主键名
    tabname=findstrnext(sql_str,'TABLE')    #抽取表名
    a=find_cont_firstparenthesis(sql_str)   #利用函数 获取第一个括号中的信息
    n=a[0]                               #获取标志位
    m=a[3]                               #获取第一个括号中的信息
    tmpm=m.replace(","," ") #将逗号替换掉
    tmpm=removespaces(tmpm)  #删除字符串中多余的空格
    list_pkcol=tmpm.split(' ')    #转为列表

    if pkname==0 or tabname==0 or n==1:
        return {'type':'addpk','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}

    else:
        tabname = namesplit(tabname)#获取表名
        pkname = namesplit(pkname)#获取主键名
        if pkname=='ADD':#alter table t1 add primary key(id) 不符合规范的
            audit_at.append((1,"请在语句中指定主键约束名,不可以使用系统自生成主键名"))
            pkname="PK_SYSAUTO"


        #print tabname,pkname

        #主键索引的列名重复 
        dict_tmp_pkcol=analyseRepeat(list_pkcol)
        for key in dict_tmp_pkcol:
            if dict_tmp_pkcol[key]>1:
                audit_at.append((2,"错误：主键约束"+pkname+"重复出现列"+key+""+str(dict_tmp_pkcol[key])+"次"))
        list_pkcol=delRepeat(list_pkcol)        #删除重复的列名
        #print list_pkcol

        #记录主键索引信息
        tabpkname = tabname+"."+pkname
        if tabpkname in at_pknames:
            return {'type':'addpk','content':orig_sql_str,'results':[(2,"错误：主键约束"+tabpkname+"在文本中重复创建")]}
        else:
            at_pknames.append(tabpkname)
            dict_at_pk_col[tabpkname]=','.join(list_pkcol) #非常重要
            at_pktabnames.append(tabname)
        #print at_pknames
        #print dict_at_pk_col
        #print at_pktabnames

        #重复建主键索引判断
        if pkname in at_pks:
            return {'type':'addpk','content':orig_sql_str,'results':[(2,"错误：主键约束"+pkname+"在文本中重复创建")]}
        else:
            at_pks.append(pkname)


        #判断主键名相关       
        if pkname.startswith(dict_config['pkname_config']):
            pass
        else:
            audit_at.append((1,"主键约束名"+str(pkname)+"不符合规范,请以"+dict_config['pkname_config']+"开头"))

        if namecheck(pkname):
            audit_at.append((2,"错误：主键约束名"+str(pkname)+namecheck(pkname)))


        #主键索引前导列判断
        firstcol=list_pkcol[0] 
        if findanystr(firstcol,'TIME')==1 or findanystr(firstcol,'DATE')==1: #判断是否时间字段
            audit_at.append((1,"主键约束"+pkname+"的前导列"+firstcol+"涉及时间字段,容易发生问题"))


        #判断前导列是否分区字段
        #dict_ct_partab[ct_tabname]=partition_type+":"+y
        if dict_ct_partab.has_key(tabname):
            parkey=dict_ct_partab[tabname].split(":")[-1] #获取分区列
            if firstcol==parkey:
                audit_at.append((1,"主键约束"+pkname+"的前导列"+firstcol+"涉及分区字段,设计不合理"))

        #主键索引的联合列个数
        if len(list_pkcol) >dict_config['pk_max_colnum']:
            audit_at.append((1,"主键约束"+pkname+"联合列数量大于"+str(dict_config['pk_max_colnum'])+",顺序:"+','.join(list_pkcol)))
        

        #主键索引对应的表是否在文本中创建 是的话判断列是否存在 
        #不是的话从线上判断表和字段是否存在 主键名是否存在等
        if dict_ct_tab_col.has_key(tabname):
            tmp_list_tabcols=dict_ct_tab_col[tabname]  #获取表的列信息 
            list_noexistscol=list(set(list_pkcol)-set(tmp_list_tabcols))
            if list_noexistscol!=[]:
                audit_at.append((2,"主键约束的列"+'、'.join(list_noexistscol)+"不存在,请检查文本中"+tabname+"建表语句的字段信息"))


        else:
            if online_info_flag==0:
                if checkobj.check_objname(tabname,"TABLE")==1:
                    audit_at.append((2,"错误：线上不存在表"+tabname))
                else:
                    if checkobj.check_objname(pkname,"INDEX")==0:
                        audit_at.append((1,"线上已有同名索引"+pkname+",主键索引无法自动创建"))

                    #相关字段是否有索引 这个比较复杂了 待完善

                    list_diff=checkobj.check_col(tabname,list_pkcol)
                    if isinstance(list_diff,list) and list_diff!=[]:
                        audit_at.append((2,"错误：线上表结构中没有如下字段："+'、'.join(list_diff)))

        
    
    #分区表的主键索引需要是local的
    if tabname in ct_part_tabnames:
        if not findanystr(sql_str,'LOCAL'):
            audit_at.append((1,"分区表不能创建全局主键索引,请添加local关键字"))
        parkey=dict_ct_partab[tabname].split(":")[-1] #获取分区列
        if parkey not in list_pkcol:
            audit_at.append((1,"分区表要创建local主键索引,请联合分区字段"+str(parkey)))



    #表空间
    if findanystr(sql_str,'TABLESPACE'):
        tabspacename=findstrnext(sql_str,'TABLESPACE')
        if tabspacename==0:
            audit_at.append((1,"表空间为空,该模块应使用 %s 表空间" %dict_config['ind_tbs']))
        elif tabspacename!=dict_config['ind_tbs']:
            audit_at.append((1,"表空间不准确,该模块应使用 %s 表空间" %dict_config['ind_tbs']))
    else:
        audit_at.append((1,"没有指定索引表空间,该模块使用 %s 表空间" %dict_config['ind_tbs']))



    #结果输出   
    if audit_at!=[]:
        return {'type':'addpk','content':orig_sql_str,'results':audit_at}
    else:
        return {'type':'addpk','content':orig_sql_str,'results':[(0,"符合规范,审核通过")]}


def addcol(sql_str):
    audit_addcol=[]
    list_col=[]
    list_datatype=[]
    orig_sql_str=sql_str
    sql_str=sql_str.upper()

    addcol_tab=findstrnext(sql_str,'TABLE')
    addcol_info=findstrnext(sql_str,'ADD')
    #print addcol_info
    if addcol_tab==0 or addcol_info==0 or (addcol_tab=='ADD'):
        return {'type':'addcol','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}

    #获取表名
    addcol_tab = namesplit(addcol_tab)

    #添加单列或者多列的情况有()
    if addcol_info.startswith('('):  
        a=find_cont_firstparenthesis(sql_str)
        if a[0]==1:
            return {'type':'addcol','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
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
    
    #没有括号的情况添加单列
    else:
        #addcol_info 列名
        list_col.append(addcol_info)

        #列类型处理
        addcol_coltype=findstrnext(sql_str,addcol_info)
        if addcol_coltype==0:
            return {'type':'addcol','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
        addcol_coltype=remove_cont_parenthesis(addcol_coltype) #去掉括号和其内容
        list_datatype.append(addcol_coltype)

        if findanystr(sql_str,'DEFAULT'):
            if not findallstr(sql_str,'NOT NULL'):
                audit_addcol.append((1,"有默认值的情况下请添加NOT NULL否则会长时间锁表"))
            tmp=findstrnext(sql_str,'DEFAULT')
            if tmp.find("''")!=-1  or tmp.find('""')!=-1:
                audit_addcol.append((1,"默认值为空"))
        if not findanystr(sql_str,'DEFAULT') and findallstr(sql_str,'NOT NULL'):
            audit_addcol.append((2,"错误：对已有表新增列不能非空并无默认值"))



      
    #print list_col  #输出所有列名 
    #print list_datatype # 输出所有字段类型 
            
    #处理重复列名
    dict_tmp_ct_cols=analyseRepeat(list_col)
    for key in dict_tmp_ct_cols:
        if dict_tmp_ct_cols[key]>1:
            audit_addcol.append((2,"错误：表"+addcol_tab+"重复创建列"+str(key)+" "+str(dict_tmp_ct_cols[key])+"次"))
    list_col=delRepeat(list_col)
        

    #判断字段类型    
    wrongcoltype = removesomeitems(list_datatype,dict_config['coltype_standard']) #配置项 去除合规的字段类型
    wrongcoltype=delRepeat(wrongcoltype)

    noexistscoltype=removesomeitems(list_datatype,dict_config['coltype_total']) #配置项
    tempmsg=""
    if wrongcoltype != []:
        tempmsg=tempmsg+"使用了"+'、'.join(wrongcoltype)+"字段类型,请尽量使用varchar2、char,number,date四种类型\n"
    if noexistscoltype!=[]:
        tempmsg=tempmsg+'、'.join(noexistscoltype)+"可能是无效的字段类型"

    if tempmsg!="":
        audit_addcol.append((1,tempmsg))


    #无需判断5个要素字段
    #判断字段名是否使用了保留关键字
    s1=set(list_col) #所有列
    s3=set(dict_config['col_reserved'])
    list_wrongname_col=list(s1&s3)#交集
    if list_wrongname_col!=[]:
        audit_addcol.append((2,"错误：字段"+'、'.join(list_wrongname_col)+"是ORACLE保留字段名"))    


    #记录列名和表名到dict_ct_tab_col
    if dict_ct_tab_col.has_key(addcol_tab):
        for key in list_col:
            if key in dict_ct_tab_col[addcol_tab]:
                audit_addcol.append((2,"错误：文本中表"+addcol_tab+"已添加列"+key))
            else:
                dict_ct_tab_col[addcol_tab].append(key)
    else:
        dict_ct_tab_col[addcol_tab]=list_col
    
    ct_exists_flag=0
    if addcol_tab in ct_tabnames:
        audit_addcol.append((1,"将该句合并到建表"+addcol_tab+"语句中执行"))
        ct_exists_flag=1

    #结合线上审核
    if online_info_flag==0 and ct_exists_flag==0:
        if checkobj.check_objname(addcol_tab,"TABLE")==1:
            audit_addcol.append((2,"错误：线上不存在"+addcol_tab+"表"))
        else:
            returnvalue=checkobj.check_col(addcol_tab,list_col)
            if isinstance(returnvalue,list) and returnvalue!=list_col:
                list_exist=list(set(list_col)-set(returnvalue))
                if list_exist!=[]:
                    audit_addcol.append((2,"错误：线上表结构中已有字段"+'、'.join(list_exist)))

    

    #结果输出   
    if audit_addcol!=[]:
        return {'type':'addcol','content':orig_sql_str,'results':audit_addcol}
    else:
        return {'type':'addcol','content':orig_sql_str,'results':[(0,"符合规范,审核通过")]}
    





def adduk(sql_str):
    audit_atuk=[]
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
    list_ukcol=tmpm.split(' ')    #转为列表


    if ukname==0 or tabname==0 or n==1:
        #alter table test add unique (col1);这种语法一般没人用
        return {'type':'adduk','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        tabname = namesplit(tabname)#获取表名
        ukname = namesplit(ukname)#获取约束名
        #print tabname,ukname
        
        #唯一索引的列名重复
        dict_tmp_ukcol=analyseRepeat(list_ukcol)
        for key in dict_tmp_ukcol:
            if dict_tmp_ukcol[key]>1:
                audit_atuk.append((2,"错误：唯一约束"+ukname+"重复出现列"+key+""+str(dict_tmp_ukcol[key])+"次"))
        list_ukcol=delRepeat(list_ukcol)#删除重复的列名
        #print list_ukcol


        #记录唯一索引信息
        tabukname = tabname+"."+ukname
        if tabukname in at_uknames:
            return {'type':'adduk','content':orig_sql_str,'results':[(2,"错误：唯一约束"+tabukname+"在文本中重复创建")]}
        else:
            at_uknames.append(tabukname)
            dict_at_uk_col[tabukname]=','.join(list_ukcol) #非常重要

        #print at_uknames
        #print dict_at_uk_col


        #重复建唯一索引判断
        if ukname in at_uks:
            return {'type':'adduk','content':orig_sql_str,'results':[(2,"错误：唯一约束"+ukname+"在文本中重复创建")]}
        else:
            at_uks.append(ukname)

        #判断唯一约束名相关       
        if ukname.startswith(dict_config['ukname_config']):
            pass
        else:
            audit_atuk.append((1,"唯一约束名"+str(ukname)+"不符合规范,请以"+dict_config['ukname_config']+"开头"))

        if namecheck(ukname):
            audit_atuk.append((2,"错误：唯一约束名"+str(ukname)+namecheck(ukname)))
  
        #唯一索引前导列判断
        firstcol=list_ukcol[0] 
        if findanystr(firstcol,'TIME')==1 or findanystr(firstcol,'DATE')==1: #判断是否时间字段
            audit_atuk.append((1,"唯一约束"+ukname+"的前导列"+firstcol+"涉及时间字段,容易发生问题"))
 

        #判断前导列是否分区字段
        #dict_ct_partab[ct_tabname]=partition_type+":"+y
        if dict_ct_partab.has_key(tabname):
            parkey=dict_ct_partab[tabname].split(":")[-1] #获取分区列
            if firstcol==parkey:
                audit_atuk.append((1,"唯一约束"+ukname+"的前导列"+firstcol+"涉及分区字段,设计不合理"))

        #唯一约束的联合列个数
        if len(list_ukcol) >dict_config['uk_max_colnum']:
            audit_atuk.append((1,"唯一约束"+ukname+"联合列数量大于"+str(dict_config['uk_max_colnum'])+",顺序:"+','.join(list_ukcol)))

        
        #唯一约束对应的表是否在文本中创建 是的话判断列是否存在 
        #不是的话从线上判断表和字段是否存在 唯一约束名是否存在等
        if dict_ct_tab_col.has_key(tabname):
            tmp_list_tabcols=dict_ct_tab_col[tabname]  #获取表的列信息 
            list_noexistscol=list(set(list_ukcol)-set(tmp_list_tabcols))
            if list_noexistscol!=[]:
                audit_atuk.append((2,"唯一约束的列"+'、'.join(list_noexistscol)+"不存在,请检查文本中"+tabname+"建表语句的字段信息"))
        else:
            if online_info_flag==0:
                if checkobj.check_objname(tabname,"TABLE")==1:
                    audit_atuk.append((2,"错误：线上不存在表"+tabname))
                else:
                    if checkobj.check_objname(ukname,"INDEX")==0:
                        audit_atuk.append((1,"线上已有同名索引"+ukname+",唯一索引无法自动创建"))

                    #相关字段是否有索引 这个比较复杂了 待完善

                    list_diff=checkobj.check_col(tabname,list_ukcol)
                    if isinstance(list_diff,list) and list_diff!=[]:
                        audit_atuk.append((2,"错误：线上表结构中没有如下字段："+'、'.join(list_diff)))



    #分区表的主键索引需要是local的
    if tabname in ct_part_tabnames:
        if not findanystr(sql_str,'LOCAL'):
            audit_atuk.append((1,"分区表不能创建全局唯一索引,请添加local关键字"))
        parkey=dict_ct_partab[tabname].split(":")[-1] #获取分区列
        if parkey not in list_ukcol:
            audit_atuk.append((1,"分区表要创建local唯一索引,请联合分区字段"+str(parkey)))

    #表空间
    if findanystr(sql_str,'TABLESPACE'):
        tabspacename=findstrnext(sql_str,'TABLESPACE')
        if tabspacename==0:
            audit_atuk.append((1,"表空间为空,该模块应使用 %s 表空间" %dict_config['ind_tbs']))
        elif tabspacename!=dict_config['ind_tbs']:
            audit_atuk.append((1,"表空间不准确,该模块应使用 %s 表空间" %dict_config['ind_tbs']))
    else:
        audit_atuk.append((1,"没有指定索引表空间,该模块使用 %s 表空间" %dict_config['ind_tbs']))


    #结果输出   
    if audit_atuk!=[]:
        return {'type':'adduk','content':orig_sql_str,'results':audit_atuk}
    else:
        return {'type':'adduk','content':orig_sql_str,'results':[(0,"符合规范,审核通过")]}


                

def renamecol(sql_str):
    audit_renamecol=[]
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    renamecol_tab=findstrnext(sql_str,'TABLE')
    renamecol_col=findstrnext(sql_str,'COLUMN')
    renamecol_col2=findstrnext(sql_str,'TO')

    if renamecol_tab==0 or renamecol_col==0 or renamecol_col2==0:
        return {'type':'renamecol','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        renamecol_tab = namesplit(renamecol_tab)#获取表名


        if dict_ct_tab_col.has_key(renamecol_tab):
            if (renamecol_col in dict_ct_tab_col[renamecol_tab]) and (renamecol_col2 not in dict_ct_tab_col[renamecol_tab]):
                dict_ct_tab_col[renamecol_tab].remove(renamecol_col)
                dict_ct_tab_col[renamecol_tab].append(renamecol_col2)
                audit_renamecol.append((1,"将该句合并到建表"+renamecol_tab+"语句中执行"))
            elif renamecol_col not in dict_ct_tab_col[renamecol_tab]:
                audit_renamecol.append((2,"错误：文本中表 %s 不存在名为 %s 的列"%(renamecol_tab,renamecol_col)))
            elif renamecol_col2 in dict_ct_tab_col[renamecol_tab]:
                audit_renamecol.append((2,"错误：文本中表 %s 已存在名为 %s 的目标列"%(renamecol_tab,renamecol_col2)))

        else:
            pass#暂不结合线上结构分析,此类变更极少而且不规范

    #结果输出   
    if audit_renamecol!=[]:
        return {'type':'renamecol','content':orig_sql_str,'results':audit_renamecol}
    else:
        return {'type':'renamecol','content':orig_sql_str,'results':[(2,"生产系统请勿更改列名,可导致应用程序受影响")]}



def modifycol(sql_str):
    #要考虑修改多列的情况
    audit_modifycol=[]
    list_col=[]
    list_datatype=[]
    orig_sql_str=sql_str
    sql_str=sql_str.upper()

    modifycol_tab=findstrnext(sql_str,'TABLE')
    modifycol_info=findstrnext(sql_str,'MODIFY')
    if modifycol_tab==0 or modifycol_info==0 or  (modifycol_tab=='MODIFY'):
        return {'type':'modifycol','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}


    modifycol_tab = namesplit(modifycol_tab)#获取表名
    #添加单列或者多列的情况有()
    if modifycol_info.startswith('('):  
        a=find_cont_firstparenthesis(sql_str)
        if a[0]==1:
            return {'type':'modifycol','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
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

    #没有括号的情况添加单列
    else:
        #modifycol_info 列名
        list_col.append(modifycol_info)

        #列类型处理
        modifycol_coltype=findstrnext(sql_str,modifycol_info)


        if modifycol_coltype==0:
            return {'type':'modifycol','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
        if modifycol_coltype=="NULL":#改为可为空
            audit_modifycol.append((1,"将字段设置成可为空,当前必须是非空，还要注意当前是否有默认值"))
        else:
            modifycol_coltype=remove_cont_parenthesis(modifycol_coltype) #去掉括号和其内容
            list_datatype.append(modifycol_coltype)

        if findanystr(sql_str,'DEFAULT'):#modify默认值 瞬间完成
            tmp=findstrnext(sql_str,'DEFAULT')
            if tmp.find("''")!=-1  or tmp.find('""')!=-1:
                audit_modifycol.append((1,"默认值为空"))
        if findanystr(sql_str,'NOT NULL'):#modif 字段改为非空
            audit_modifycol.append((1,"添加该字段非空约束,需要表中该字段没有任何空值"))



    #print list_col  #输出所有列名 
    #print list_datatype # 输出所有字段类型 


    if modifycol_tab in ct_tabnames:
        audit_modifycol.append((1,"将该句合并到建表"+modifycol_tab+"语句中执行"))
        
        noexistscol=[]
        for item in list_col:
            if item not in dict_ct_tab_col[modifycol_tab]:
                noexistscol.append(item)
        if noexistscol!=[]:
            audit_modifycol.append((2,"错误：文本中表 %s 不存在名为 %s 的列"%(modifycol_tab,'、'.join(noexistscol)) ))
    else:
        if online_info_flag==0:
            if checkobj.check_objname(modifycol_tab,"TABLE")==1:
                audit_modifycol.append((2,"错误：线上不存在表"+modifycol_tab))
            else:
                list_diff=checkobj.check_col(modifycol_tab,list_col)
                if isinstance(list_diff,list) and list_diff!=[]:
                    audit_modifycol.append((2,"错误：线上表结构中没有如下字段："+'、'.join(list_diff)))

    #结果输出   
    if audit_modifycol!=[]:
        return {'type':'modifycol','content':orig_sql_str,'results':audit_modifycol}
    else:
        return {'type':'modifycol','content':orig_sql_str,'results':[(0,"符合规范,审核通过（注意不能缩小字段长度）")]}


def dropcol(sql_str):
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    audit_dropcol=[]
    dropcol_tab=findstrnext(sql_str,'TABLE')
    dropcol_col=findstrnext(sql_str,'COLUMN')

    if dropcol_tab==0 or dropcol_col==0:
        return {'type':'dropcol','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        dropcol_tab = namesplit(dropcol_tab)#获取表名
        #print dropcol_tab
        #print dropcol_col
        if dict_ct_tab_col.has_key(dropcol_tab):
            if dropcol_col in dict_ct_tab_col[dropcol_tab]:
                dict_ct_tab_col[dropcol_tab].remove(dropcol_col)
                audit_dropcol.append((1,"将该句合并到建表"+dropcol_tab+"语句中执行"))
            else:
                audit_dropcol.append((2,"错误:文本中表 %s 不存在名为 %s 的列"%(dropcol_tab,dropcol_col)))
        else:
            pass#暂不结合线上结构分析,此类变更极少而且不规范

    #结果输出   
    if audit_dropcol!=[]:
        return {'type':'dropcol','content':orig_sql_str,'results':audit_dropcol}
    else:
        return {'type':'dropcol','content':orig_sql_str,'results':[(2,"生产环境不允许删除字段,请与DBA沟通")]}


def dropconst(sql_str):
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    audit_dropconst=[]
    dropconst_tab=findstrnext(sql_str,'TABLE')
    dropconst_const=findstrnext(sql_str,'CONSTRAINT')

    if dropconst_tab==0 or dropconst_const==0:
        return {'type':'dropconst','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        dropconst_tab = namesplit(dropconst_tab)#获取表名
        #print dropconst_tab
        #print dropconst_const
        return {'type':'dropconst','content':orig_sql_str,'results':[(2,"生产环境不允许删除约束,请与DBA沟通")]}


def droptab(sql_str):
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    audit_droptab=[]
    droptab_name=findstrnext(sql_str,'TABLE')

    if droptab_name==0:
        return {'type':'droptab','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        droptab_name = namesplit(droptab_name)#获取表名
        #print droptab_name
        if dict_ct_tab_col.has_key(droptab_name):
            audit_droptab.append((1,"直接清理文本中的建表语句"))
        else:
            if online_info_flag==0:
                if checkobj.check_objname(droptab_name,"TABLE")==1:
                    audit_droptab.append((2,"错误：线上不存在表"+droptab_name))

    #结果输出   
    if audit_droptab!=[]:
        return {'type':'droptab','content':orig_sql_str,'results':audit_droptab}
    else:
        return {'type':'droptab','content':orig_sql_str,'results':[(2,"生产环境不允许删除表,请与DBA沟通")]}



def dropseq(sql_str):
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    audit_dropseq=[]
    dropseq_name=findstrnext(sql_str,'SEQUENCE')

    if dropseq_name==0:
        return {'type':'dropseq','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        #处理序列名
        dropseq_name = namesplit(dropseq_name)
        return {'type':'dropseq','content':orig_sql_str,'results':[(2,"生产环境不允许删除序列,请与DBA沟通")]}
            

def dropidx(sql_str):
    orig_sql_str=sql_str
    sql_str=sql_str.upper()
    audit_dropind=[]
    dropind_name=findstrnext(sql_str,'INDEX')

    if dropind_name==0:
        return {'type':'dropidx','content':orig_sql_str,'results':[(2,"错误：无法正常解析语法")]}
    else:
        #处理索引名
        dropind_name = namesplit(dropind_name)
        return {'type':'dropidx','content':orig_sql_str,'results':[(2,"生产环境不允许删除索引,请与DBA沟通")]}




  #####################
#Part4 汇总审核功能函数#
  #####################
  
#汇总类审核函数
def summary():
    list_return=[]
    funcnamelist=['summary_parttab','summary_pk','summary_idx',
    'summary_comtab','summary_comcol','summary_sqltype']
    for funcname in funcnamelist:
        dict_re = eval(funcname)()
        if dict_re:
            list_return.append(dict_re)
        else:
            continue
    return list_return



def summary_sqltype():
    list_audit_text=[]
    totalddl=0
    for key in sqltype_count:
        if sqltype_count[key]!=0:
            totalddl+=sqltype_count[key]
            list_audit_text.append(str(key)+":"+str(sqltype_count[key]))
        else:
            pass
    if totalddl!=0:
        list_audit_text.insert(0,"搜索到"+str(totalddl)+"句DDL,分类如下：")#在头部插入
    if list_audit_text!=[]:
        audittext="\n".join(list_audit_text)
        return {'type':'summary_sqltype'+str(totalddl),'content':"审核语句类型统计",'results':[(3,audittext)]}



def summary_idx():
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



    #统计文本创建的表 没有任何索引
    for tabname in ct_tabnames:
        if not tabind.has_key(tabname):
            audit_ci_summary.append((1,"表"+tabname+"上面没有任何索引"))
    #统计一个表上的索引总个数超过2个的并输出 并将有2个索引或以上的表名收集
    for key in tabind:
        indnum = len(tabind[key])
        #print indnum
        if indnum>int(dict_config['max_indnum_eachtable']): #配置项
            audit_ci_summary.append((1,"表"+key+"上面有"+str(indnum)+"个索引,大于"+str(dict_config['max_indnum_eachtable'])+"个"))


    #冗余的索引处理#
    dict_all_ind_col=mergedict(dict_ci_ind_col,dict_at_uk_col)#{'表名.索引名':'col1,col2'}
      
    for tabname in tabind:#记录表的全部索引名 {T1:[I1_1,I1_2,I1_3],T2:[I2_1,I2_2]}
        list_indcols=[]
        for indname in tabind[tabname]:
            list_indcols.append(dict_all_ind_col[tabname+"."+indname])

        #print tabname #表
        #print list_indcols# 索引列  ['col1,col2','col2']
        reden_flag=0
        for item in list_indcols:
            list_indcols_tmp=copy.deepcopy(list_indcols)
            list_indcols_tmp.remove(item)
            #print item
            #print list_indcols_tmp
            for key in list_indcols_tmp:
                if key.startswith(item):
                    reden_flag=1

        if reden_flag==1:
            audit_ci_summary.append((1,"表"+tabname+"上面有冗余索引"))
                       
    if audit_ci_summary!=[]:  
        return {'type':'summary_idx','content':"索引情况分析",'results':audit_ci_summary}





def summary_comtab():
    dictoutput = {}
    audit_co_summary = []
    for tabname in ct_tabnames:
        if tabname not in comtab_tabnames:
            audit_co_summary.append((1,"表 %s 没有表级注释语句"%tabname))
    if audit_co_summary!=[]:
        return {'type':'summary_comtab','content':"表注释分析",'results':audit_co_summary}


def summary_comcol():
    #print dict_comcol_tab_col #记录列注释语句的表和表的列 {'T1': ['COL1', 'COL2']}
    audit_col_summary = []
    for tabname in dict_ct_tab_col:
        if dict_comcol_tab_col.has_key(tabname):
            cl_collist=dict_ct_tab_col[tabname]
            co_collist=dict_comcol_tab_col[tabname]
            #求差集
            lostcollist = list(set(cl_collist).difference(set(co_collist)))
            if lostcollist!=[]:
                lostcolstr = ','.join(lostcollist)
                audit_col_summary.append((1,"表 %s 少了注释列 %s"%(tabname,lostcolstr)))
        else:
            audit_col_summary.append((1,"表 %s 没有任何列注释语句,请添加"%tabname))
            

    if audit_col_summary!=[]:
        return {'type':'summary_comcol','content':"列注释分析",'results':audit_col_summary}



def summary_pk():
    #建主键语句审核汇总
    audit_at_summary=[]
    #表建议都要有主键
    lostpktab = set(ct_tabnames).difference(set(at_pktabnames))
    if len(lostpktab)>0:
        for tabname in lostpktab:
            audit_at_summary.append((1,"表 %s 没有主键,表必须要有主键,请添加"%tabname))

    if audit_at_summary!=[]:
        return {'type':'summary_pk','content':"主键情况分析",'results':audit_at_summary}



def summary_parttab():
    audit_part = []
    ct_nopart_tabnames=removesomeitems(ct_tabnames,ct_part_tabnames)
    #print ct_nopart_tabnames
    #分区建议  比如表名涉及ORDER LOG等关键字 但没有分区
    for item in ct_nopart_tabnames:
        if item.find("LOG")==-1 and  item.find("ORDER")==-1:
            pass
        else:
            audit_part.append((1,"建议将日志表或订单表"+item+"进行分区"))
    if audit_part!=[]:
        return {'type':'summary_parttab','content':"分区表情况分析",'results':audit_part}




        

if __name__ == "__main__": #非网页版测试使用  需要import最后三个项目
    filepath=os.getcwd()    #获取当前文本的路径
    print "当前路径：\n",filepath,"\n" #打印当前路径

    filecount=0  
    print "待审核的文件:"
    for root,dirs,files in os.walk(filepath):#遍历当前路径下的所有文件情况
        #print root  #根目录
        #print dirs  #根目录下的文件夹 
        #print files #根目录下的文件  
        for  filename in files:
            if filename.endswith(".sql"):     #判断必须是.sql文件
                filecount=filecount+1
                fulfilename=os.path.join(root,filename)
                print filecount," ",fulfilename     #显示所有的sql文件 并使用数字排序号

                filesqltext=open(fulfilename,"r")
                sqltext=filesqltext.read()#读取全部内容到返回str
                #print filesqltext.readline()#读取单行 反复执行
                #print filesqltext.readlines()#读取所有行并返回list
                #print chardet.detect(sqltext)['encoding']
                sqltext=sqltext.decode(chardet.detect(sqltext)['encoding']).encode("utf-8")
                auditresult=process_sqlfile(sqltext,dict_config,"xulijia","xulijia",'192.168.136.88','1521','testdbw')  #开始审核  




                make_txt(str(filename.replace(".sql",""))+'_audit_result.txt',auditresult)


                



