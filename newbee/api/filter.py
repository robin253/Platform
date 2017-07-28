import rest_framework_filters as filters
from rest_framework import filters as source_filter

from newbee.models import *


class FunctiongroupFilter(filters.FilterSet):
    name = filters.CharFilter(name="fun_groupname")
    class Meta:
        model = Functiongroup
        fields = ['fun_groupname']

class HostFilter(filters.FilterSet):
    function_group = filters.RelatedFilter(FunctiongroupFilter, name='function_group')
    ip = filters.CharFilter(name='ip')
    port = filters.CharFilter(name='port')
    class Meta:
        model = Host
        fields=['function_group','ip','port']

class RoleFilter(filters.FilterSet):
    name = filters.CharFilter(name="rolename")
    class Meta:
        model = Role
        fields = ['rolename']

class Exe_groupFilter(filters.FilterSet):
    name = filters.CharFilter(name="exe_groupname")
    class Meta:
        model = Role
        fields = ['name']

class MissionFilter(filters.FilterSet):
    name = filters.CharFilter(name="exe_groupname")
    class Meta:
        model = Mission
        fields = ['exe_groupname']
