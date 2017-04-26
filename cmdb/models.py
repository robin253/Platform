# -*- coding:utf-8 -*-
from django.db import models
from datetime import datetime


#模型相关常量
db_usage_choices = (('pro','生产'),('dev','开发'),('test','测试'),('qa','压测'))

db_type_choices = (('oracle', 'ORACLE'),('mysql',  'MySQL'),('redis',  'REDIS'))  #第一个是存入数据库的值 第二个是ADMIN后台展示的值

yn_choices= (('n','否'),('y','是'))



# Create your models here.
#注意
#一个字段名不能是一个Python保留字
#一个字段名不能包含连续的一个以上的下划线，因为那是Django查询语句的语法


# 所有表的公共字段
class PublicColumns(models.Model):#每个数据模型都是 django.db.models.Model 的子类
    id = models.AutoField(primary_key=True) #AutoField指一个能够根据可用ID自增的 IntegerField
    created_by = models.CharField(max_length=32, blank=True)#charField的max_length必填
    created_at = models.DateTimeField(auto_now_add=True) #默认值
    #DateField日期 DateTimeField时间日期 auto_now_add 第一次产生时字段设置为当前日期
    updated_by = models.CharField(max_length=32, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    #auto_now每次对象保存时设置为当前日期

    class Meta:#Meta是一个内部类
        abstract = True#这个属性是定义当前的模型类是不是一个抽象类。所谓抽象类是不会对应数据库表的
                       #一般我们用它来归纳一些公共属性字段，然后继承它的子类可以继承这些字段


class T_CMDB_DBINFO(PublicColumns): 
    #part1
    db_name=models.CharField(max_length=64, help_text="db_type ip port servicename db_usage等的别称 确定一个实例")
    db_type= models.CharField(max_length=32,choices=db_type_choices,help_text="数据库类型") 
    ipadress=models.CharField(max_length=64)
    port=models.CharField(max_length=8)
    servicename=models.CharField(max_length=32,blank=True,help_text="服务名,仅ORACLE需要")
    db_usage = models.CharField(max_length=10, choices=db_usage_choices, help_text="数据库环境")
    dbausername=models.CharField(max_length=64,blank=True,help_text="数据库DBA维护账户") 
    dbapassword=models.CharField(max_length=64,blank=True,help_text="数据库DBA维护账号密码")
    sysuser=models.CharField(max_length=64,help_text="操作系统账号")
    syspassword=models.CharField(max_length=64,help_text="操作系统账号密码")
    directory=models.CharField(max_length=64,blank=True,help_text="oracle 导入导出路径")
    #part2
    skema=models.CharField(max_length=64,help_text="数据库schema") 
    username=models.CharField(max_length=64,help_text="连接该skema的用户") 
    password=models.CharField(max_length=64,help_text="连接该skema的用户密码") 
    privilege_flag=models.CharField(max_length=1, choices=yn_choices,help_text="权限分离标志")
    appuser=models.CharField(max_length=64,blank=True,help_text="应用用户") 
    appuser_password=models.CharField(max_length=64,blank=True,help_text="应用用户密码") 
    readuser=models.CharField(max_length=64,blank=True,help_text="只读用户") 
    readuser_password=models.CharField(max_length=64,blank=True,help_text="只读用户密码")
    default_data_tbs=models.CharField(max_length=64,blank=True,help_text="数据表空间")
    default_ind_tbs=models.CharField(max_length=64,blank=True,help_text="索引表空间")
    #part3
    app_name=models.CharField(max_length=64, help_text="对应应用模块名")
    remark=models.CharField(max_length=128,blank=True, help_text="备注")  #blank=True 允许是空字符串   mysql中存入'' 
                                                     #null=True 可为null 这和数据库字段定义相关了 默认not null

    #part1  part2 part3 分别是： 实例  schema  应用模块 的概念  概念上说是逐层一对多的   

    class Meta:
        db_table='T_CMDB_DBINFO' 
        unique_together = (("db_name","skema","app_name"),)   #设置唯一约束
        verbose_name='数据库信息表'
        verbose_name_plural='数据库信息表'




