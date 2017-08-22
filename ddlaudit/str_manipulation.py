#!/usr/bin/python
# -*- coding: UTF-8 -*-
#字符串的处理

import re
from re import search
import time
from functools import wraps

def fn_timer(function):
  @wraps(function)
  def function_timer(*args, **kwargs):
    t0 = time.time()
    result = function(*args, **kwargs)
    t1 = time.time()
    print ("Total time running %s: %s seconds" %
        (function.func_name, str(t1-t0))
        )
    return result
  return function_timer

#removespaces函数
#连续两个空格及以上的只保留一个 并删除字符串前后的所有空格
def removespaces(inputstr):
   tmp_list=inputstr.split(' ') #以空格为分隔符转为列表
   #print tmp_list
   tmp_list2=[]
   for item in tmp_list:  #列表中有内容的项放入到列表tmp_list2中
      if len(item)==0:
         pass
      else:
         tmp_list2.append(item)
   re_str=' '.join(tmp_list2)  #将列表tmp_list2的项用空格间隔转为字符串
   return re_str

# findallstr函数
#判断字符串中是否有指定的一个或者多个字符 全部找到返回1  否则返回0
def findallstr(str,*vartuple):
    a=0
    b=0
    for var in vartuple:
        b=b+1
        if str.find(var)!=-1:  #在str中找字符串var开始的位置 如果没有找到那么显示-1
            a=a+1
    if a==b:
        return 1
    else:
        return 0


# findanystr函数
#判断字符串中是否有指定的一个或者多个字符 只要找到一个或以上则返回1 否则返回0

def findanystr(str,*vartuple):
    a=0
    for var in vartuple:
        if str.find(var)!=-1:
            a=a+1
    if a>0:
        return 1
    else:
        return 0



#findstrnext函数
#找字符串某个关键词后面的词 空格作为词的分隔符号  返回0那么说明不存在关键词或者关键词后面没有词了 
def findstrnext(strinput,findstr):
    tmp_list=strinput.split(" ")
    if tmp_list.count(findstr)>=1:
        #print "number",tmp_list.count(findstr)
        try:
            #print tmp_list.index(findstr)
            returnstr=tmp_list[tmp_list.index(findstr)+1]
        except:
            return 0
        else:
            return returnstr
    else:
        return 0
        
#findstrbefore函数
#找字符串某个关键词前面的词 空格作为词的分隔符号  返回0那么说明不存在关键词或者关键词前面没有词了 

def findstrbefore(strinput,findstr):
    tmp_list=strinput.split(" ")
    if tmp_list.count(findstr)>=1:
        if tmp_list.index(findstr)-1>=0:
            return tmp_list[tmp_list.index(findstr)-1]
        else:
            return 0
    else:
        return 0




#bracklet_split函数
#对字符串以，分隔为列表，可避免k1,k2(k3,k4),k5这种情况的分割异常 [k1,k2(k3,k4),k5] 
def bracklet_split(sql_str):
    #去掉开头的左右括号
    str_start = 0
    str_end = len(sql_str)
    if sql_str[str_start]=='(' and sql_str[str_end-1]==')':
        str_start = 1
        str_end-=1
    #字符串分割
    tmp_queue=[]
    tmp_str=''
    res_list = []
    for posi in xrange(str_start,str_end,1):
        if sql_str[posi]=='(':
            tmp_queue.append('(')
            tmp_str+='('
        elif sql_str[posi]==')':
            tmp_queue.pop()
            tmp_str+=')'
        else:
            if len(tmp_queue)>=1:
                tmp_str+=sql_str[posi]
            elif sql_str[posi]==',':
                res_list.append(tmp_str)
                tmp_str=''
            else:
                tmp_str+=sql_str[posi]
    res_list.append(tmp_str)
    return res_list




#remove_comma_childstr函数
#对字符串以，分隔为列表,如果列表元素中有相关关键字那么删除这个元素 返回字符串     
def remove_comma_childstr(str,keyword):
   tmp_list=bracklet_split(str) #以,分隔为列表
   #print tmp_list
   tmp_list2=[]
   for item in tmp_list:  #列表中有某个关键字的项过滤
      if item.find(keyword)==-1:
         tmp_list2.append(item)
   #print tmp_list2
   re_str=','.join(tmp_list2)  #将列表tmp_list2的项用逗号间隔转为字符串
   return re_str






#removechildstr函数
#在字符串中删除特定部分，分别用两个子字符串来确认删除部分的开头和结尾

def removechildstr(str,strstart,strend):
   p1=str.find(strstart)  #找到开头的位置
   p2=str.find(strend)  #找到结尾的位置
   #print p1,p2
   if p1==-1 or p2==-1:
      return str
   elif p1>=p2:
      return str
   else:
      ptail=p2+len(strend)
      #print p1,ptail
      return str[0:p1]+str[ptail:]

#a="/* time is money */create table t1 (id number,name varchar2(20);"
#b=removechildstr(a,"/*","*/")
#print b
#create table t1 (id number,name varchar2(20);


##将字符串owner.object_name 以.分隔并返回object_name  
def namesplit(namestr):
  namelist = namestr.split('.')
  return namelist[-1]

#检查对象名长度不超过30并不能用数字开头
def namecheck(str):
  tmplist=[]
  if len(str)>30:
    tmplist.append("长度超过30个字符")
  if search("^[0-9]",str):
    tmplist.append("用数字开头")
  tmpstr=','.join(tmplist)
  return tmpstr


  
if __name__=="__main__":
    mystr = "(nihao,danshi,zhe,zhende,bushi(zhe,zhende,bushi),yigehao,fangshi,(wo,know))"
    mystr2 = "nihao,woshishei,nishishei,women shizenyangde,danshi varchar(10),nihao number(20)"
    print bracklet_split(mystr)
    print bracklet_split(mystr2)
    #['nihao', 'danshi', 'zhe', 'zhende', 'bushi(zhe,zhende,bushi)', 'yigehao', 'fangshi', '(wo,know)']
    #['nihao', 'woshishei', 'nishishei', 'women shizenyangde', 'danshi varchar(10)', 'nihao number(20)']
     
    sql_str='''create index I_telereport_cell_phone_MOBILE on TEST (MOBILE)  online tablespace TBS_CRPAY_IDX'''


    print findstrbefore(sql_str.upper(),'TEST') #抽取索引名


