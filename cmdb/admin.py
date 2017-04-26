# -*- coding:utf-8 -*-
from django.contrib import admin

#这样可以在后台编辑models
from models import *


class T_CMDB_DBINFO_ADMIN(admin.ModelAdmin):
    list_display = ( 'db_name','db_type','ipadress','port','servicename','db_usage',\
                    'dbausername','sysuser','directory',\
                    'skema','username','privilege_flag','appuser','readuser','app_name')
    search_fields = ['db_name','ipadress','servicename','skema','username','app_name']  
    list_filter = ['db_type','db_usage']            
    ordering = ['db_name','skema','app_name']  


admin.site.register(T_CMDB_DBINFO,T_CMDB_DBINFO_ADMIN)   



