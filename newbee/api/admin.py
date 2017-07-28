# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from import_export import resources,fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportMixin, ImportMixin, ExportActionModelAdmin,ImportExportModelAdmin,ExportMixin
from models import *
from django.core.paginator import Paginator


class FunctiongroupResource(resources.ModelResource):
    class Meta:
        model = Functiongroup
        skip_unchanged = True
        fields = ('id','fun_groupname')


class FunctiongroupAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = FunctiongroupResource
    list_display=('id','fun_groupname')
    search_fields=('fun_groupname',)
    list_filter = ('fun_groupname',)
    list_per_page = 10
    ordering = ('id','fun_groupname')
    fields = ('fun_groupname',)

class HostResource(resources.ModelResource):
    function_group= fields.Field(column_name='function_group', attribute='function_group',
                   widget=ForeignKeyWidget(Functiongroup, 'fun_groupname'))
    class Meta:
        model = Host
        skip_unchanged = True
        fields = ('id','hostname','ip','port','function_group','status','host_var')

class HostAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = HostResource
    list_display=('id','hostname','ip','port','function_group','status','host_var','created_date','modified_date')
    search_fields=('hostname',)
    list_filter = ('hostname',)
    list_per_page = 10
    date_hierarchy = 'created_date'
    ordering = ('id','hostname','ip','port','function_group','status','created_date')
    fields = ('hostname','ip','port','function_group','host_var','status')

class RoleResource(resources.ModelResource):
    class Meta:
        model = Role
        skip_unchanged = True
        fields = ('id','rolename','role_var','detail','stepnum')

class RoleAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = Role
    list_display=('id','rolename','role_var','detail','created_date',)
    search_fields=('rolename',)
    list_filter = ('rolename',)
    list_per_page = 10
    ordering = ('id','rolename','created_date')
    fields = ('rolename','role_var','detail','stepnum')

class ExeuserResource(resources.ModelResource):
    class Meta:
        model = Exeuser
        skip_unchanged = True
        fields = ('id','username','password','exe_port')

class ExeuserAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = Exeuser
    list_display=('id','username','exe_port','created_date',)
    search_fields=('username',)
    list_filter = ('username',)
    list_per_page = 10
    ordering = ('id','username','created_date')
    fields = ('username','password','sudo_password','exe_port')

# 以下几个函数为注册函数，注册后，就能实现在后台显示相关的板块

admin.site.register(Functiongroup,FunctiongroupAdmin)
admin.site.register(Host,HostAdmin)
admin.site.register(Role,RoleAdmin)

# admin.site.register(Mission)
admin.site.register(Exeuser,ExeuserAdmin)
