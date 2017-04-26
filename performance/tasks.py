#!/bin/env python
# -*- coding: UTF-8 -*-

from celery import shared_task
import time
import sendwechat 

@shared_task  #忽略装饰器 像平时那样调用函数也是可以的
def add(x,y):
    return x+y

@shared_task
def mul(x,y):
    return x*y


@shared_task 
def xsum(numbers):
    return sum(numbers)

@shared_task 
def sendwe(content):
    time.sleep(10)
    wechat_sender=sendwechat.WeChat()
    msg_dict=wechat_sender.send_messages(content)#调用方法发送信息 并返回信息
    return msg_dict