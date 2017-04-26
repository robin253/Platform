#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import random

#dmlaudit 产生一个随着时间递增的批次号
def dmlaudit_batch():
    nowTime=datetime.datetime.now().strftime("%Y%m%d%H%M%S");#生成当前时间
    #print  nowTime
    part1=nowTime[2:-6]
    part2=nowTime[-6::]

    randomNum=random.randint(0,99);#生成的随机整数
    if randomNum<10: 
        randomNum=str(0)+str(randomNum); 
    
    return part1+"M_"+part2+str(randomNum)

#ddlaudit的批次号
def ddlaudit_batch(db_type,release_date,skema):
	if db_type=='oracle':
	    dbtypeabbr='ORA'
	elif db_type=='mysql':
		dbtypeabbr="MYSQL"
	return dbtypeabbr+"_"+skema+"_"+release_date






