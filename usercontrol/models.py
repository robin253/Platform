# -*- coding:utf-8 -*-
from django.db import models

#公共字段
class PublicColumns(models.Model):#每个数据模型都是 django.db.models.Model 的子类
    id = models.AutoField(primary_key=True) #AutoField指一个能够根据可用ID自增的 IntegerField
    created_by = models.CharField(max_length=32, blank=True)#charField的max_length必填
    created_at = models.DateTimeField(auto_now_add=True) #默认值
    #DateField日期 DateTimeField时间日期 auto_now_add 第一次产生时字段设置为当前日期
    updated_by = models.CharField(max_length=32, blank=True)
    #blank=True 允许是空字符串   mysql中存入''
    #null=True 可为null 这和数据库字段定义相关了 默认not null
    updated_at = models.DateTimeField(auto_now=True)
    #auto_now每次对象保存时设置为当前日期

    class Meta:#Meta是一个内部类
        abstract = True#这个属性是定义当前的模型类是不是一个抽象类。所谓抽象类是不会对应数据库表的
                       #一般我们用它来归纳一些公共属性字段，然后继承它的子类可以继承这些字段


class UserPerm(PublicColumns):
    name=models.CharField(max_length=30,help_text="姓名") #生产上要求这是全局唯一的
    phone=models.CharField(max_length=18,help_text="手机")

    class Meta:
        db_table='t_user_permission'
        verbose_name='用户权限控制'
        verbose_name_plural='用户权限控制'








