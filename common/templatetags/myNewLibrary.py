# -*- coding:utf-8 -*-
from django import template #创建register变量
register =template.Library()

import chardet


#自定义的过滤器就是一个带1，2个参数的python函数，一个参数放变量值，一个用来放选项值
@register.filter(name='limit') #注册这个过滤器 name是对应使用名
def limit(var, arg):
    #print type(var)
    if type(var)==type("str"): #如果不是unicode那么要转换一下
        var=var.decode("UTF-8")
    return var[0:int(arg)]

#{{ var|limit:"arg" }} var是变量值，"arg"是选项值
#以上限制显示字符串个数


#换行符显示到html
@register.filter(name='newline') 
def newline(var):
    return var.replace("\n","<br>")




#将值转换为中文显示DML
@register.filter(name='displaychinese')
def displaychinese(var):
    dict_trans={'valid':'通过','invalid':'不通过',\
    'init':'待执行','suc':'成功','fail':'失败','noexe':'不可执行','doing':'执行中',\
    'qualified':'通过','semi-qualified':'待DBA评估','unqualified':'不通过','cancel':'取消'}
    if var in dict_trans:
        return dict_trans[var]
    return ''

#将值转换为中文显示DDL
@register.filter(name='ddldisplaychinese')
def ddldisplaychinese(var):
    dict_trans={0:'通过',1:'待修改',2:'不通过',
               'wait':'待审核','fail':'失败','suc':'成功',
               'start':'发起','submit':'审核中','freeze':'审核通过','release':'已发布','cancel':'已取消',  #批次状态
               }  

    if var in dict_trans:
        return dict_trans[var]
    return ''


#str to list
@register.filter(name='strtolist')
def strtolist(var):
    return eval(var)

    

@register.filter(name="displaychoices") 
def displaychoices(value,arg):
	return  apply(eval('value.get_'+arg+'_display'),())  
    #GENDER_CHOICES = ( (u'M', u'Male'), (u'F', u'Female'), )
    #gender = models.CharField(max_length=2, choices=GENDER_CHOICES)
    #p.save() 
    #p.gender # M
    #p.get_gender_display() #Male
	#eval(str) 用来计算在字符串中的有效Python表达式,并返回一个对象
	#apply(func,())执行函数

    #{{p|displaychoices:'gender'}}


#{% load %}只允许导入注册app目录下的模板库这样做是为了保证你的模板库可以不被其它Django程序使用





