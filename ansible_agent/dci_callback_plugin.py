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

import mock

# jobstate = mock.Mock()
# dci_file = mock.Mock()
#
# create_mock = mock.Mock()
# jobstate.create.return_value = create_mock
# create_mock.json.return_value = {'jobstate': {'id': '6a067184-8e41-11e6-b2c0-c85b7636c33f'}}

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

        self._no_dci = False

    # get the name of each task's commands
    def v2_playbook_on_task_start(self, task, is_conditional):
        super(CallbackModule, self).v2_playbook_on_task_start(task, is_conditional)
        if self._no_dci:
            return


    def v2_runner_on_failed(self, result, ignore_errors=False):
        """Event executed when a command failed. Create the final jobstate
        on failure."""
        super(CallbackModule, self).v2_runner_on_failed(result, ignore_errors)

        if self._no_dci:
            return

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

        if 'no_dci' in play.get_vars():
            self._no_dci = True
            return

        status = play.get_vars()['dci_status']
        self._current_comment = play.get_vars()['dci_comment']
        self._job_id = play.get_variable_manager().extra_vars['job_id']
        log_directory = play.get_variable_manager().extra_vars['local_logs']

        new_state = jobstate.create(
            self._dci_context,
            status=status,
            comment=self._current_comment,
            job_id=self._job_id).json()
        self._current_jobstate_id = new_state['jobstate']['id']
        print('******* %s' % self._current_jobstate_id)
        jobstate_id_path = '%s/%s/jobstate_id' % (log_directory, status)
        with open(jobstate_id_path, 'w') as jobstate_id_file:
            jobstate_id_file.write(self._current_jobstate_id)
