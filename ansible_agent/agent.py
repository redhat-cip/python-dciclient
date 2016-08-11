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


import os

from ansible import inventory
from ansible import vars
from ansible.executor import playbook_executor
from ansible.parsing import dataloader

from ansible.utils.display import Display


class Options(object):
    def __init__(self, verbosity=None, inventory=None, listhosts=None, subset=None, module_paths=None, extra_vars=None,
                 forks=None, ask_vault_pass=None, vault_password_files=None, new_vault_password_file=None,
                 output_file=None, tags="all", skip_tags=None, one_line=None, tree=None, ask_sudo_pass=None, ask_su_pass=None,
                 sudo=None, sudo_user=None, become=None, become_method=None, become_user=None, become_ask_pass=None,
                 ask_pass=None, private_key_file=None, remote_user=None, connection=None, timeout=None, ssh_common_args=None,
                 sftp_extra_args=None, scp_extra_args=None, ssh_extra_args=None, poll_interval=None, seconds=None, check=None,
                 syntax=None, diff=None, force_handlers=None, flush_cache=None, listtasks=None, listtags=None, module_path=None):
        self.verbosity = verbosity
        self.inventory = inventory
        self.listhosts = listhosts
        self.subset = subset
        self.module_paths = module_paths
        self.extra_vars = extra_vars
        self.forks = forks
        self.ask_vault_pass = ask_vault_pass
        self.vault_password_files = vault_password_files
        self.new_vault_password_file = new_vault_password_file
        self.output_file = output_file
        self.tags = tags
        self.skip_tags = skip_tags
        self.one_line = one_line
        self.tree = tree
        self.ask_sudo_pass = ask_sudo_pass
        self.ask_su_pass = ask_su_pass
        self.sudo = sudo
        self.sudo_user = sudo_user
        self.become = become
        self.become_method = become_method
        self.become_user = become_user
        self.become_ask_pass = become_ask_pass
        self.ask_pass = ask_pass
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.connection = connection
        self.timeout = timeout
        self.ssh_common_args = ssh_common_args
        self.sftp_extra_args = sftp_extra_args
        self.scp_extra_args = scp_extra_args
        self.ssh_extra_args = ssh_extra_args
        self.poll_interval = poll_interval
        self.seconds = seconds
        self.check = check
        self.syntax = syntax
        self.diff = diff
        self.force_handlers = force_handlers
        self.flush_cache = flush_cache
        self.listtasks = listtasks
        self.listtags = listtags
        self.module_path = module_path


class Runner(object):

    def __init__(self, playbook, options=None, verbosity=0):

        if options is None:
            self.options = Options()
            self.options.verbosity = verbosity

        self.loader = dataloader.DataLoader()
        self.variable_manager = vars.VariableManager()

        self.inventory = inventory.Inventory(
            loader=self.loader,
            variable_manager=self.variable_manager,
            host_list='/etc/ansible/hosts'
        )
        self.variable_manager.set_inventory(self.inventory)

        # Playbook to run, from the current working directory.
        pb_dir = os.path.abspath('.')
        playbook_path = "%s/%s" % (pb_dir, playbook)

        self.pbex = playbook_executor.PlaybookExecutor(
            playbooks=[playbook_path],
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords={})

    def run(self, job_id):
        """Run the playbook and returns the playbook's stats."""
        self.variable_manager.extra_vars = {'job_id': job_id}
        self.pbex.run()
        return self.pbex._tqm._stats


if __name__ == '__main__':

    runner = Runner(playbook='site.yml', verbosity=0)
    stats = runner.run('kikoolol')
    jumpbox_stats = stats.summarize('jumpbox')
    if jumpbox_stats['unreachable'] > 0 or jumpbox_stats['failures'] > 0:
        print("Failed :(\n")
    else:
        print("Succeed :)\n")
