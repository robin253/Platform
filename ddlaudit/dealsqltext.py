#!/bin/env python
# coding=UTF-8
from common import splitor
from str_manipulation import removespaces #连续两个空格及以上的只保留一个 并删除字符串前后的所有空格


#处理待审核的sql文本格式,主要功能：
#分隔所有本文语句为单语句的列表
#去除单行和多行注释 hint信息
#tab和换行符都改为空格    
#左括号前添加空格   右括号后添加空格    逗号前后空格删除
#删除多余的空格 

def dealsqltext(sqltext):
    lexerSplitor = splitor.LexerSplitor()
    list_sql=[]
    for sql in lexerSplitor.split(sqltext):
        sql=lexerSplitor.remove_sqlcomment(sql)# 去除单行和多行注释 hint信息
        sql = sql.replace('\t',' ') #tab符改为空格
        sql = sql.replace('\n',' ') #换行符改为空格
        sql = sql.replace(' , ',',')#逗号前后空格删除
        sql = sql.replace(', ',',')
        sql = sql.replace(' ,',',')
        sql = sql.replace('(',' (') #左括号前添加空格   右括号后添加空格
        sql = sql.replace(')',') ')
        sql=removespaces(sql)#删除多余的空格 
        #sql=sql.upper() #转为大写 这个不对 注释语句里面的值是小写的呢
        list_sql.append(sql)
        #换行符的问题


    return list_sql