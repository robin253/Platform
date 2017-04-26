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


class InefficientSql(PublicColumns): 
    skema=models.CharField(max_length=30,help_text="数据库schema") #生产上要求这是全局唯一的
    inst_id=models.IntegerField(help_text="实例号") 
    sql_id=models.CharField(max_length=13, help_text="sql_id") 
    sql_text=models.TextField(help_text="sql文本") 
    plan_hash_value=models.BigIntegerField(help_text="sql的执行计划编号")  
    first_load_time=models.CharField(max_length=19, help_text="父游标产生时间") 
    last_active_time=models.CharField(max_length=19, help_text="某子游标上次执行时间")
    executions=models.IntegerField(help_text="执行次数") 
    avg_time_ms=models.IntegerField(help_text="单次执行平均时间") 
    avg_gets_mb=models.IntegerField(help_text="单次执行平均逻辑读") 
    avg_reads_mb=models.IntegerField(help_text="单次执行平均物理读") 
    status=models.CharField(max_length=10,default='init',help_text="语句审核状态") 


    class Meta:
        db_table='t_sqlstat_inefficientsql' 
        unique_together = (("skema","inst_id","sql_id"),)   #设置唯一约束
        verbose_name='低效sql信息'
        verbose_name_plural='低效sql信息'








