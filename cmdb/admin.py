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




class DBMeta_ADMIN(admin.ModelAdmin):
    fields = ['db_desc','db_type','admin_ip','db_port','service_name','domain_name','rw_flag','data_port']
    list_display = ( 'db_desc','db_type','admin_ip','db_port','service_name','domain_name')
    search_fields = ('service_name','admin_ip','domain_name')
    ordering = ['db_desc','admin_ip']
    def save_model(self, request, obj, form, change):

        ip = obj.admin_ip
        print ip
        ip_list = ip.split('.')
        data_ip_list = [ip_list[0],'29']+ip_list[2:]
        service_ip_list = [ip_list[0],'28']+ip_list[2:]

        data_ip = '.'.join(data_ip_list)
        service_ip = '.'.join(service_ip_list)
        obj.data_ip = data_ip
        obj.service_ip = service_ip
        super(DBMeta_ADMIN,self).save_model(request, obj, form, change)

admin.site.register(DBMeta,DBMeta_ADMIN)
admin.site.register(T_CMDB_DBINFO,T_CMDB_DBINFO_ADMIN)



