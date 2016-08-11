# -*- coding: utf-8 -*-
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

from ansible.plugins import callback

from dciclient.v1.api import context as dci_context
from dciclient.v1.api import job
from dciclient.v1.api import jobstate
from dciclient.v1.api import file as dci_file


class CallbackModule(callback.CallbackBase):
    def __init__(self):
        super(CallbackModule, self).__init__()

        self._dci_context = dci_context.build_dci_context(
        'http://127.0.0.1:5000',
        'admin',
        'admin')

        self._current_jobstate_id = None
        self._job_id = None
        self._current_step = 0
        self._filename_prefix = ''

    # get the name of each task's commands
    def v2_playbook_on_task_start(self, task, is_conditional):
        print("* v2_playbook_on_task_start()")
        print("** task name: %s\n" % task.get_name())

    # get the result of each task commands
    def v2_runner_on_ok(self, result, **kwargs):
        """Event executed after each command when it succeed. Get the output
        of the command and create a file associated to the current jobstate."""
        if 'stdout_lines' not in result._result:
            return
        print("*** v2_runner_on_ok()")
        output = '\n'.join(result._result['stdout_lines']) + '\n'
        dci_file.create(
            self._dci_context,
            name=self._filename_prefix + '_' + str(self._current_step),
            content=output,
            mime='text/plain',
            jobstate_id=self._current_jobstate_id)
        self._current_step += 1
        print("*** result: %s\n" % output)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """Event executed when a command failed. Create the final jobstate
        on failure."""
        print("* v2_runner_on_failed()")
        jobstate.create(
            self._dci_context,
            status='failure',
            comment=str(result._result['cmd']),
            job_id=self._job_id)

    def v2_playbook_on_play_start(self, play):
        """Event executed before each play. Create a new jobstate and save
        the current jobstate id."""
        print("* v2_playbook_on_play_start()")
        self._current_step = 0
        self._filename_prefix = play.get_vars()['dci_log_prefix']
        status = play.get_vars()['dci_status']
        comment = play.get_vars()['dci_comment']
        self._job_id = play.get_variable_manager().extra_vars['job_id']

        new_state = jobstate.create(
            self._dci_context,
            status=status,
            comment=comment,
            job_id=self._job_id).json()
        self._current_jobstate_id = new_state['jobstate']['id']
        print("** jobstate: %s\n** comment: %s\n" % (status, comment))

    def v2_playbook_on_start(self, playbook):
        """Event executed before running the playbook. Schedule a job
        and save the job id."""
        print("* v2_playbook_start()")
