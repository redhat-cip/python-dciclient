#!/usr/bin/env python
#  -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook import Playbook
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager


from callback_plugin.dci import CallbackModule as DciCallback


Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check'])
# initialize needed objects
variable_manager = VariableManager()
loader = DataLoader()
options = Options(connection=None, module_path=None, forks=100, become=None, become_method=None, become_user=None, check=False)

# Instantiate our ResultCallback for handling results as they come in
results_callback = DciCallback()

# create inventory and pass to var manager
inventory = Inventory(loader=loader,
                      variable_manager=variable_manager,
                      host_list='/etc/ansible/hosts')
variable_manager.set_inventory(inventory)

playbook = Playbook.load('/home/yassine/git/dci/python-dciclient/ansible_agent/site.yml', variable_manager=variable_manager, loader=loader)

pbex = PlaybookExecutor(playbooks='/home/yassine/git/dci/python-dciclient/ansible_agent/site.yml',
                        inventory=inventory, variable_manager=variable_manager, loader=loader, options=None, passwords=None)

results = pbex.run()
print(results)


# try:
#     tqm = TaskQueueManager(
#         inventory=inventory,
#         variable_manager=variable_manager,
#         loader=loader,
#         options=options,
#         passwords=None,
#         stdout_callback=results_callback,
#     )
#     for p in playbook.get_plays():
#         tqm.run(p)
# finally:
#     if tqm is not None:
#         tqm.cleanup()
