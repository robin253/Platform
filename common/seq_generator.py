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


#ddlaudit生成随机密码

def GenerateRandomPasswd(length):
    if length<8:
        print '密码最少8位'
        return 0
    pass_str_alpha = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    pass_str_word = ',.!@#$%^&*()_+-=0987654321'

    #生成密码的头和尾
    pass_head = random.choice(tuple(pass_str_alpha))
    pass_end = random.choice(tuple(pass_str_alpha))
    pass_middle = ''

    #生成字母密码
    for i in range(length-5):
        pass_middle = pass_middle + random.choice(tuple(pass_str_alpha))

    #生成特殊字符数字密码
    for i in range(3):
        pass_middle = pass_middle + random.choice(tuple(pass_str_word))

    #打乱密码
    pass_middle_list = list(pass_middle)
    random.shuffle(pass_middle_list)

    #合成密码
    password = pass_head+''.join(pass_middle_list)+pass_end
    return password



