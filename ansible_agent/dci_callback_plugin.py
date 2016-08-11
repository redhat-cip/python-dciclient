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

from ansible.plugins.callback.default import CallbackModule as DefaultCallback

from dciclient.v1.api import jobstate
from dciclient.v1.api import file as dci_file


class CallbackModule(DefaultCallback):
    """Inherit from the stdout default callback plugin and simply adds
    DCI calls."""
    def __init__(self, dci_context):
        super(CallbackModule, self).__init__()

        self._dci_context = dci_context

        # the current jobstate id
        self._current_jobstate_id = None
        # the job id of the run which is passed as extra vars
        self._job_id = None

    # get the name of each task's commands
    def v2_playbook_on_task_start(self, task, is_conditional):
        super(CallbackModule, self).v2_playbook_on_task_start(task, is_conditional)

    # get the result of each task commands
    def v2_runner_on_ok(self, result, **kwargs):
        """Event executed after each command when it succeed. Get the output
        of the command and create a file associated to the current jobstate."""
        super(CallbackModule, self).v2_runner_on_ok(result, **kwargs)

        if 'stdout_lines' in result._result:
            output = '\n'.join(result._result['stdout_lines']) + '\n'
        elif 'msg' in result._result:
            output = '\n'.join(result._result['msg']) + '\n'
        else:
            output = str(result._result)
        output = output.encode('UTF-8')

        if result._task.get_name() != 'setup' and output != '\n':
            dci_file.create(
                self._dci_context,
                name=result._task.get_name(),
                content=output,
                mime='text/plain',
                jobstate_id=self._current_jobstate_id)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """Event executed when a command failed. Create the final jobstate
        on failure."""
        super(CallbackModule, self).v2_runner_on_failed(result, ignore_errors)

        output = result._result['stderr'] + '\n'
        new_state = jobstate.create(
            self._dci_context,
            status='failure',
            comment=self._current_comment,
            job_id=self._job_id).json()
        self._current_jobstate_id = new_state['jobstate']['id']

        if result._task.get_name() != 'setup' and output != '\n':
            dci_file.create(
                self._dci_context,
                name=result._task.get_name(),
                content=output.encode('UTF-8'),
                mime='text/plain',
                jobstate_id=self._current_jobstate_id)

    def v2_playbook_on_play_start(self, play):
        """Event executed before each play. Create a new jobstate and save
        the current jobstate id."""
        super(CallbackModule, self).v2_playbook_on_play_start(play)

        status = play.get_vars()['dci_status']
        self._current_comment = play.get_vars()['dci_comment']
        self._job_id = play.get_variable_manager().extra_vars['job_id']

        new_state = jobstate.create(
            self._dci_context,
            status=status,
            comment=self._current_comment,
            job_id=self._job_id).json()
        self._current_jobstate_id = new_state['jobstate']['id']
