#!/bin/env python
# -*- coding: UTF-8 -*-

from celery import shared_task,task
import time


@task(name="sum_two_numbers")  #忽略装饰器 像平时那样调用函数也是可以的
def add(x,y):
    return x+y

@shared_task
def mul(x,y):
    return x*y


@shared_task 
def xsum(numbers):
    return sum(numbers)


@task(ignore_result=True,max_retries=1,default_retry_delay=10)#taskname
def just_print():
    print "Print from celery task"