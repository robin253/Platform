# -*- coding:utf-8 -*-
import os

#dmlaudit相关配置常量


#表分区展示 每页展示的行数
ONE_PAGE_OF_DATA=6 

#备份文件路径
backup_filepath=os.path.join(os.path.dirname(__file__),'backupfiles').replace('\\', '/')#\变成/ 

#微信通知开关
sendwechat_flag=0


