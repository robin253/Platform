# -*- coding:utf-8 -*-
from django.contrib import admin

# Register your models here. 这样可以在后台编辑models
from models import *




class T_DMLAUDIT_BATCH_INFO_ADMIN(admin.ModelAdmin):
    list_display = (             
        'audit_user','audit_batch','audit_time','app_name','db_type','sqlamount','batch_status','evaluator',\
        'execute_status','executor')
    search_fields = ['audit_user', 'audit_batch','app_name']  
    list_filter = ['audit_user','app_name','db_type','batch_status']     
    list_display_links = ['audit_batch']  
    ordering = ['audit_user', 'audit_batch']  


class T_DMLAUDIT_BATCH_DETAIL_ADMIN(admin.ModelAdmin):
    list_display = (              #后台展示列表
        'audit_batch','sqlnum','sqltext','sqltype','grammar','gra_failreason','exetime','rowaffact','audit_status')
    search_fields = ['audit_batch__audit_batch']  #后台搜索框 可以搜索的列   # 查询外键信息 http://blog.csdn.net/davidsu33/article/details/51672163
    list_filter = ['audit_status']     #后台过滤工具栏 用于过滤的列
    list_display_links = ['audit_batch']  # 设置页面上哪个字段可单击进入详细页面
    ordering = ['audit_batch', 'sqlnum']    #后台展示的排序字段 


admin.site.register(T_DMLAUDIT_BATCH_INFO,T_DMLAUDIT_BATCH_INFO_ADMIN)   
admin.site.register(T_DMLAUDIT_BATCH_DETAIL,T_DMLAUDIT_BATCH_DETAIL_ADMIN) 


