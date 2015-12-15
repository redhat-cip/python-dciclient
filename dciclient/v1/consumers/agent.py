# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Red Hat, Inc
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

from dciclient.v1.handlers import file
from dciclient.v1.handlers import job
from dciclient.v1.handlers import jobstate
from dciclient.v1.handlers import remoteci

import fcntl
import os
import pprint
import select
import StringIO
import subprocess
import sys


class Agent(object):
    """DCI base agent class"""

    # The different possible states for a job
    PRE_RUN = 'pre-run'
    RUNNING = 'running'
    POST_RUN = 'post-run'
    SUCCESS = 'success'
    FAILURE = 'failure'

    def __init__(self, session, remoteci_id):
        self._session = session
        self._l_jobstate = jobstate.JobState(self._session)
        self._l_file = file.File(self._session)
        self.remoteci_id = remoteci_id
        self.team_id = self._get_team_id_of_remoteci(remoteci_id)
        self.job_id = None

    def _get_team_id_of_remoteci(self, remoteci_id):
        l_remoteci = remoteci.RemoteCI(self._session)
        registered_remoteci = l_remoteci.get(id=remoteci_id).json()
        return registered_remoteci['remoteci']['team_id']

    def schedule_job(self):
        l_job = job.Job(self._session)
        scheduled_job = l_job.schedule(self.remoteci_id).json()
        self.job_id = scheduled_job['job']['id']
        job_full_data = l_job.get_full_data(self.job_id)
        print('* Job id: %s\n' % self.job_id)
        print('* Job data:\n')
        pprint.pprint(job_full_data)
        print('\n')
        return self.job_id, job_full_data

    def send_state(self, status, comment=None):
        l_jobstate = jobstate.JobState(self._session)
        job_state = l_jobstate.create(status=status, comment=comment,
                                      job_id=self.job_id, team_id=self.team_id)
        return job_state.json()['jobstate']['id']

    def run_command(self, cmd, cwd, jobstate_id):
        output = StringIO.StringIO()
        pipe_process = subprocess.Popen(cmd, cwd=cwd,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

        fcntl.fcntl(pipe_process.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        inputs = [pipe_process.stdout]
        outputs = []

        while True:
            readable, writable, exceptional = select.select(inputs, outputs,
                                                            inputs, 1)
            if not readable:
                break
            read = pipe_process.stdout.read().decode('UTF-8', 'ignore')
            if len(read) == 0:
                break
            print(read)
            output.write(read)

        # equivalent to pipe_process.wait(), avoid deadlock, see Popen doc.
        pipe_process.communicate()

        self._l_file.create(name='_'.join(cmd), content=output.getvalue(),
                            mime='text/plain', jobstate_id=jobstate_id,
                            team_id=self.team_id)
        output.close()
        return pipe_process.returncode

    def run_commands(self, cmds, cwd, jobstate_id):
        for cmd in cmds:
            rc = self.run_command(cmd, cwd, jobstate_id)
            if rc != 0:
                self.send_state(Agent.FAILURE)
                return

    def pre_run(self):
        return None

    def run(self):
        return None

    def post_run(self):
        return None

    def run_agent(self):
        """Run the agent business logic"""
        if not self.job_id:
            print('Schedule a job before running the agent logic.')
            sys.exit(1)

        pre_run_cmds = self.pre_run()
        if pre_run_cmds:
            pre_run_jobstate_id = self.send_state(Agent.PRE_RUN,
                                                  'Starting pre-run setup.')
            self.run_commands(pre_run_cmds['cmds'], pre_run_cmds['cwd'],
                              pre_run_jobstate_id)

        run_cmds = self.run()
        if run_cmds:
            run_jobstate_id = self.send_state(Agent.RUNNING,
                                              'Starting running setup.')
            self.run_commands(run_cmds['cmds'], run_cmds['cwd'],
                              run_jobstate_id)

        post_run_cmds = self.post_run()
        if post_run_cmds:
            post_run_jobstate_id = self.send_state(Agent.POST_RUN,
                                                   'Starting post-run setup.')
            self.run_commands(post_run_cmds['cmds'], post_run_cmds['cwd'],
                              post_run_jobstate_id)
