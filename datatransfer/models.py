# -*- coding:utf-8 -*-
from django.db import models



# 所有表的公共字段
class PublicColumns(models.Model):
    id = models.AutoField(primary_key=True) 
    created_by = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_by = models.CharField(max_length=32, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True





class T_DATATRANSFER_EXPDP(PublicColumns): 
    launch_user = models.CharField(max_length=64,help_text="EXPDP任务发起人") 
    db_name=models.CharField(max_length=64, help_text="db_type ip port servicename db_usage等的别称 确定一个实例")
    skema=models.CharField(max_length=64,help_text="数据库schema") 
    job_name=models.CharField(max_length=128,db_index=True,help_text="EXPDP任务号")
    tables=models.TextField(help_text="导出的表清单")   
    tablespace=models.TextField(help_text="导出的表涉及的表空间")
    segments_bytes=models.CharField(max_length=32, help_text="表大小预估，单位:M")
    directory=models.CharField(max_length=128, help_text="数据库导出directory")
    dumpfilepath=models.CharField(max_length=128, help_text="数据库导出directory的路径")
    parallel=models.CharField(max_length=16,blank=True, help_text="并行度")
    expdpcommand=models.TextField(help_text="导出命令")
    logfile=models.TextField(help_text="EXPDP日志")   
    status=models.CharField(max_length=8,help_text="导出任务执行状态") 

    class Meta:
        db_table='T_DATATRANSFER_EXPDP'  

        verbose_name='EXPDP任务记录表'
        verbose_name_plural='EXPDP任务记录表'

    def __unicode__(self):
        return('job_name:%s' %(self.job_name))
