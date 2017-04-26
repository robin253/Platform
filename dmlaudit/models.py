# -*- coding:utf-8 -*-
from django.db import models
from datetime import datetime


#模型相关常量
db_type_choices = (('oracle', 'ORACLE'),('mysql',  'MySQL'),('redis',  'REDIS')) 
sqltype_choices=(('insert_select',  'INSERT_SELECT'),('insert', 'INSERT'),('update', 'UPDATE'),('delete', 'DELETE'),\
                ('other','OTHER'))


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




class T_DMLAUDIT_BATCH_INFO(PublicColumns): 
    audit_user = models.CharField(max_length=64) 
    audit_batch=models.CharField(max_length=64,db_index=True)
    audit_time=models.DateTimeField(auto_now_add=True)
    app_name=models.CharField(max_length=64)
    db_type= models.CharField(max_length=32,choices=db_type_choices)
    allsqltext=models.TextField()   #全文本
    sqlamount=models.IntegerField() #该批次的sql条数
    batch_status=models.CharField(max_length=16,blank=True) #总批次的审核结果
    evaluator=models.CharField(max_length=64,blank=True)   #审核人
    execute_status=models.CharField(max_length=8,default='init') 
    executor=models.CharField(max_length=64,blank=True)   #执行人
    exe_failreason=models.CharField(max_length=128,blank=True)#执行失败原因 记录第几句失败

    class Meta:
        db_table='T_DMLAUDIT_BATCH_INFO'  

        verbose_name='DML批次信息表'
        verbose_name_plural='DML批次信息表'

    def __unicode__(self):
        return('audit_batch:%s,batch_status:%s' %(self.audit_batch,self.batch_status))


class T_DMLAUDIT_BATCH_DETAIL(PublicColumns): #继承前面的抽象类

    audit_batch=models.ForeignKey(T_DMLAUDIT_BATCH_INFO)
    sqlnum=models.IntegerField()#整数IntegerField
    sqltext = models.TextField()#比较长的使用TextField 不限制max_length
    sqltype= models.CharField(max_length=16,choices=sqltype_choices)
    grammar=models.CharField(max_length=8)  
    gra_failreason=models.CharField(max_length=256,blank=True)
    sqlplan= models.TextField(blank=True)
    exetime=models.CharField(max_length=32,blank=True) 
    rowaffact=models.IntegerField(default=0)
    audit_status=models.CharField(max_length=16)      #单句审核结果

    class Meta:
        db_table='T_DMLAUDIT_BATCH_DETAIL'  #如果没有指定该选项的话Django会使用： app_name + '_' + model_class_name 
        #db_tablespace=''  可以指定表空间

        verbose_name='DML批次详情表'#起一个更可读的名字
        verbose_name_plural='DML批次详情表'#模型的复数形式 如果不指定Django会自动在模型名称后加一个s 
        #app_label='' #你的模型类不在默认的应用程序包下的models.py文件中，这时候你需要指定这个参数

    def __unicode__(self):
        return('%s' %(self.audit_batch))



