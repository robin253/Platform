# -*- coding:utf-8 -*-
from django.db import models
from datetime import datetime


#模型相关常量
db_type_choices = (('oracle', 'ORACLE'),('mysql',  'MySQL')) 

#sql语句类型统计 目前共计18种
sqltype_choices=(
                 ('createtab_select',  'CREATETAB_SELECT'),
                 ('createtab', 'CREATETAB'),
                 ('createidx', 'CREATEIDX'),
                 ('createseq', 'CREATESEQ'),
                 ('commenttab','COMMENTTAB'),
                 ('commentcol','COMMENTCOL'),
                 ('truncate','TRUNCATE'),
                 ('addpk','ADDPK'),
                 ('adduk','ADDUK'),
                 ('addcol','ADDCOL'),
                 ('renamecol','RENAMECOL'),
                 ('modifycol','MODIFYCOL'),
                 ('dropcol','DROPCOL'),
                 ('dropconst','DROPCONST'),
                 ('droptab','DROPTAB'),
                 ('dropidx','DROPIDX'),
                 ('dropseq','DROPSEQ'),
                 ('othersql','OTHERSQL'),
                 )




# 所有表的公共字段
class PublicColumns(models.Model):
    id = models.AutoField(primary_key=True) 
    created_by = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_by = models.CharField(max_length=32, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
                       

class T_DDLAUDIT_BATCH_INFO(PublicColumns): 
    audit_user = models.CharField(max_length=64,help_text="审核提交人") 
    audit_batch=models.CharField(max_length=64,db_index=True,help_text="审核批次号")
    release_date=models.IntegerField(help_text="发布日期",blank=True)
    audit_time=models.DateTimeField(auto_now_add=True)
    app_name=models.CharField(max_length=64,help_text="应用模块名")
    db_type= models.CharField(max_length=32,choices=db_type_choices,help_text="数据库类型")
    allsqltext=models.TextField(help_text="审核文本")   
    sqlamount=models.IntegerField(help_text="批次DDL条数")
    batch_status=models.CharField(max_length=16,blank=True,help_text="批次状态") 
    evaluator=models.CharField(max_length=64,blank=True,help_text="review人")  
    execute_status=models.CharField(max_length=8,help_text="执行状态") 
    executor=models.CharField(max_length=64,blank=True,help_text="执行人")   
    exe_failreason=models.CharField(max_length=128,blank=True,help_text="执行失败原因")#记录第几句失败

    class Meta:
        db_table='T_DDLAUDIT_BATCH_INFO'  

        verbose_name='DDL批次信息表'
        verbose_name_plural='DDL批次信息表'

    def __unicode__(self):
        return('audit_batch:%s,batch_status:%s' %(self.audit_batch,self.batch_status))



class T_DDLAUDIT_BATCH_DETAIL(PublicColumns):

    audit_batch=models.ForeignKey(T_DDLAUDIT_BATCH_INFO)
    sqlnum=models.IntegerField()
    sqltext = models.TextField()
    sqltype= models.CharField(max_length=16,choices=sqltype_choices)
    audit_result=models.TextField(help_text="审核结果")  
    audit_status= models.IntegerField(help_text="审核结果状态：通过，待修改，不通过")

    class Meta:
        db_table='T_DDLAUDIT_BATCH_DETAIL'  

        verbose_name='DDL批次详情表'
        verbose_name_plural='DDL批次详情表'

    def __unicode__(self):
        return('%s' %(self.audit_batch))



