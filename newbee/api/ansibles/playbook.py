#!/bin/env python
#-*- coding: utf-8 -*-

"""
   The main execute class of playbook
"""

__authors__ = [
    '"Lian Shifeng" <lianshifeng-it@bestpay.com.cn>',
]

import json
import os
import MySQLdb
from datetime import datetime

from global_var import *
from callback import *
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook import Playbook
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.stats import AggregateStats
from ansible.plugins.callback import CallbackBase
from ansible.utils.unicode import to_bytes



class MyRun(object):
    '''
    rewrite run method
    '''

    MSG_HEAD = '''%(time)s | PLAY [%(playname)s] ********************************************************************\n'''
    MSG_FORMAT = '''%(time)s | TASK [%(task_name)s] *******************************************************************
    %(info)s
    \n'''
    MSG_RESULT = '''%(time)s | PLAY RECAP *********************************************************************
    %(summary)s
    \n'''
    def __init__(self,*args,**kwargs):
        self.inventory = None
        self.variable_manager = None
        self.loader = None
        self.options = None
        self.passwords = None
        self.results_callback = None
        self.__initialize()
        self.results = {}

    def __initialize(self):

        Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax','connection','module_path', 'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args','become','become_method','become_user','verbosity', 'check'])
        self.variable_manager = VariableManager()
        self.loader = DataLoader()
        self.options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='smart', module_path=None, forks=100, remote_user='bestpay', private_key_file=None, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True, become_method='sudo', become_user='root', verbosity=None, check=False)

        self.passwords = {}
        self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list=HOST_PATH)
        self.variable_manager.set_inventory(self.inventory)

    def run(self,mission_id,role_name,exe_group):
        '''
        create play with tasks actually run it
        '''
        tqm = None
        try:
            retry_path = ENTRY_PATH
            inventory_path = [retry_path]
            self.results_callback = ResultCallback(mission_id)
            extra_vars = {}
            extra_vars['host_list'] = exe_group
            extra_vars['role_name'] = role_name
            extra_vars['run_id'] = mission_id
            self.variable_manager.extra_vars = extra_vars
            pbex = PlaybookExecutor(
                playbooks=inventory_path,
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
            )

            pbex._tqm._stdout_callback = self.results_callback
            result = pbex.run()
        finally:
            if tqm is not None:
                tqm.cleanup()

    def log(self,path,msg):
        with open(path,"ab") as fd:
            fd.write(msg)

    def get_results(self,mission_id):
        path = os.path.join(MISSION_LOG,mission_id)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = self.results_callback.res
        playname = result[-1]['play']['name']
        data = result[-1]['tasks']
        summary = json.dumps(self.results_callback.summary,indent=4)
        head_msg = {
            'time': datetime.now(),
            'playname': playname
        }
        head_log = to_bytes(self.MSG_HEAD % head_msg)
        self.log(path,head_log)
        for task in data:
            taskName = task["task"]["name"]
            rep = task["hosts"]
            output = {
                'time': datetime.now(),
                'task_name': taskName,
                'info': json.dumps(rep,indent=4,sort_keys=True)
            }
            info_msg = to_bytes(self.MSG_FORMAT % output)
            self.log(path,info_msg)
        result_msg = {
            'time': datetime.now(),
            'summary': summary
        }
        result_log = to_bytes(self.MSG_RESULT % result_msg)
        self.log(path,result_log)
        return  summary


