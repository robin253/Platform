from django.db import models
from newbee.abstract.models import CommonModel
import uuid



class Functiongroup(CommonModel):
    # id = models.AutoField(primary_key=True)
    fun_groupname = models.CharField(max_length=128,unique=True)
    def __unicode__(self):
        return self.fun_groupname
class Host(CommonModel):
     id = models.AutoField(primary_key=True)
     hostname = models.CharField(max_length=128,unique=True)
     ip = models.GenericIPAddressField(db_index=True,unique=True)
     port = models.IntegerField()
     function_group = models.ForeignKey(Functiongroup)
     status = models.IntegerField()
     host_var = models.CharField(max_length=512)
     # create_time = models.DateTimeField()
     # modified_time = models.DateTimeField()

class Role(CommonModel):
     id = models.AutoField(primary_key=True)
     rolename = models.CharField(max_length=128,unique=True)
     role_var = models.CharField(max_length=1024,blank=True)
     detail = models.CharField(max_length=1024)
     stepnum = models.IntegerField(default=1)
     class Meta:
         db_table='T_NEWBEE_ROLE'

class Exe_group(CommonModel):
     id = models.AutoField(primary_key=True)
     exe_groupname = models.CharField(max_length=128,unique=True)
     group_var = models.CharField(max_length=256,blank=True)
     detail = models.CharField(max_length=1024,blank=True)
     class Meta:
           ordering = ['-id']

class Host_exe_group(CommonModel):
     hostid= models.ForeignKey(Host)
     exe_groupid= models.ForeignKey(Exe_group)


class Mission(CommonModel):
     id = models.AutoField(primary_key=True)
     rolename = models.CharField(max_length=128)
     exe_groupname = models.CharField(max_length=128)
     exe = models.CharField(max_length=128)
     log = models.CharField(max_length=128)
     status = models.IntegerField(default=0)

     def __unicode__(self):
        return self.exe_groupname
     class Meta:
           ordering = ['-id']

class Num(models.Model):
        id = models.AutoField(primary_key=True)
        num = models.IntegerField(default=0)

class Exeuser(CommonModel):
        id = models.AutoField(primary_key=True)
        username = models.CharField(max_length=128)
        password = models.CharField(max_length=256)
        sudo_password = models.CharField(max_length=256,blank=True)
        exe_port = models.IntegerField()
        def __unicode__(self):
            return self.username
