# -*- coding:utf-8 -*-
from django.contrib import admin



from models import UserPerm
from django.contrib.auth.models import Permission

admin.site.register(Permission)


class T_USER_PERMISSION_ADMIN(admin.ModelAdmin):
    list_display = ('name','phone')#后台展示列表
    search_fields = ['name',]  #后台搜索框 可以搜索的列   # 查询外键信息 http://blog.csdn.net/davidsu33/article/details/51672163
    list_filter = ['name',]     #后台过滤工具栏 用于过滤的列
    list_display_links = ['name',]  # 设置页面上哪个字段可单击进入详细页面
    ordering = ['name',]    #后台展示的排序字段


admin.site.register(UserPerm,T_USER_PERMISSION_ADMIN)


