#!/bin/evn python
#-*- coding: utf-8 -*-

"""
   Backward callback moudle
"""

__authors__ = [
    '"Lian Shifeng" <lianshifeng-it@bestpay.com.cn>',
]

import MySQLdb
# from db import *
from newbee.models import FuncRecord
from ansible.executor.stats import AggregateStats
from ansible.plugins.callback import CallbackBase


class ResultCallback(CallbackBase):
        '''
        rewrite callback by owner，inherit Callbackbase
        '''
        def __init__(self,*args,**kwargs):
                #super(ResultCallback,self).__init__(*args,**kwargs)
                self.res = []
                self.summary = {}
                self.num = []
 		self.id = None
		for arg in args:
			self.id = arg

        def _new_play(self, play):
                return {
                        'play': {
                                'name': play.name,
                                'id': str(play._uuid)
                        },
                        'tasks': []
                }

        def _new_task(self, task):
                return {
                        'task': {
                        'name': task.name,
                        'id': str(task._uuid)
                },
                'hosts': {}
                }

        def v2_playbook_on_play_start(self, play):
		'''
		  play 开始入口
		'''

                self.res.append(self._new_play(play))

        def v2_playbook_on_task_start(self, task, is_conditional):
		'''
		  任务开始入口
		'''
                self.res[-1]['tasks'].append(self._new_task(task))
                self.num.append(self._new_task(task)['task']['name'])
                tk = len(self.num)
                # update('api_num',tk,self.id)
                obj,created = FuncRecord.objects.get_or_create(id=self.id,defaults={'num':tk})
                if not created:
                    obj.num = 500
                    obj.save()

        def v2_runner_on_ok(self, result, **kwargs):
		'''
		   处理运行成功的任务

		'''

                host = result._host
                rlt = result._result
                if rlt['invocation']:
                        del rlt['invocation']
                self.res[-1]['tasks'][-1]['hosts'][host.name] = rlt

        def v2_runner_on_unreachable(self, result):
		'''
                  处理运行不可达的任务

		'''
                host = result._host
                self.res[-1]['tasks'][-1]['hosts'][host.name] = result._result

        def v2_runner_on_failed(self, result,  *args, **kwargs):
                '''
	         处理运行失败的任务

                '''
                host = result._host
                self.res[-1]['tasks'][-1]['hosts'][host.name] = result._result


        def v2_playbook_on_stats(self, stats):
                """ Display info about playbook statistics """

                hosts = sorted(stats.processed.keys())
                v = []

                for h in hosts:
                        s = stats.summarize(h)
                        self.summary[h] = s
                        if s['failures'] > 0 or s['unreachable'] > 0:
                                v.append(0)
                        else:
                                v.append(1)
                if sum(v) == 0:
                    obj,created = FuncRecord.objects.get_or_create(id=self.id,defaults={'num':500})
                    if not created:
                        obj.num = 500
                        obj.save()
			# update('api_num',500,self.id)

