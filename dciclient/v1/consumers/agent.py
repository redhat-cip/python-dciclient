# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Red Hat, Inc
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

from dciclient.v1.consumers import dciconsumer
from dciclient.v1.handlers import file
from dciclient.v1.handlers import job
from dciclient.v1.handlers import jobdefinition
from dciclient.v1.handlers import jobstate
from dciclient.v1.handlers import remoteci

import subprocess


class Agent(dciconsumer.DCIConsumer):
    """A DCI agent class"""

    def __init__(self, dci_cs_url, login, password, remoteci_name):
        super(Agent, self).__init__(dci_cs_url, login, password)
        self.remoteci_id, self.team_id = self._retrieve_context(remoteci_name)
        self.job_id, self.jobinformation = self._retrieve_jobinformation()

    def _retrieve_context(self, remoteci_name):
        """Retrieve a remoteci id and team_id by the remote_ci name"""
        l_remoteci = remoteci.RemoteCI(self._s)

        remoteci_data = l_remoteci.get(remoteci_name).json()['remoteci']

        return remoteci_data['id'], remoteci_data['team_id']

    def _retrieve_jobinformation(self):
        """Retrieve job informations"""
        job_embed = ['jobdefinition']

        l_job = job.Job(self._s)
        l_jobdefinition = jobdefinition.JobDefinition(self._s)

        job_data = l_job.schedule(remoteci_id=self.remoteci_id).json()['job']
        jobdefinition_data = (
            l_job .get(id=job_data['id'], embed=','.join(job_embed))
            .json()['job']['jobdefinition']
        )
        component_data = (
            l_jobdefinition.get_components(jobdefinition_data['id'])
            .json()['components']
        )

        jobinformation = {
            'job': job_data,
            'jobdefinition': jobdefinition_data,
            'components': component_data,
            'data': l_job.get_full_data(job_data['id']),
        }

        return job_data['id'], jobinformation

    def _get_state_hash(self, status, comment):
        return {'job_id': self.job_id,
                'status': status,
                'comment': comment,
                'team_id': self.team_id}

    def _run_command(self, cmd, cwd, jobstate_id):
        """Run the actual command and upload the output """
        l_file = file.File(self._s)
        ret_value = 0

        cwd = cmd[0]['cwd'] if 'cwd' in cmd[0] else cwd
        if 'cwd' in cmd[0]:
            cmd = cmd[1:]

        try:
            flat_cmd = ' '.join(cmd)
            output = subprocess.check_output(flat_cmd, shell=True, cwd=cwd)
            l_file.create(name='_'.join(cmd),
                          content=output,
                          mime='text/plain',
                          jobstate_id=jobstate_id,
                          team_id=self.team_id)
        except subprocess.CalledProcessError as e:
            l_file.create(name=e.cmd,
                          content=e.output,
                          mime='text/plain',
                          jobstate_id=jobstate_id,
                          team_id=self.team_id)
            ret_value = -1
        except (OSError, IOError, TypeError):
            ret_value = -1

        return ret_value

    def run_agent(self, run, pre_run=None, post_run=None):
        """Run the agent business logic"""
        failure = False
        l_jobstate = jobstate.JobState(self._s)
        kwargs = self._get_state_hash('new', 'Starting run agent')
        l_jobstate.create(**kwargs)

        if pre_run:
            kwargs = (
                self
                ._get_state_hash('pre-run', 'Starting pre_run setup')
            )
            pre_run_jobstate_id = (
                l_jobstate
                .create(**kwargs).json()['jobstate']['id']
            )
            for cmd in pre_run['cmds']:
                rc = (
                    self
                    ._run_command(cmd, pre_run['cwd'], pre_run_jobstate_id)
                )
                if rc != 0:
                    kwargs = (
                        self
                        ._get_state_hash('failure', 'Failure in pre_run setup')
                    )
                    l_jobstate.create(**kwargs)
                    failure = True

        if not failure:
            kwargs = self._get_state_hash('running', 'Starting run setup')
            run_jobstate_id = (
                l_jobstate.create(**kwargs)
                .json()['jobstate']['id']
            )
            for cmd in run['cmds']:
                rc = self._run_command(cmd, run['cwd'], run_jobstate_id)
                if rc != 0:
                    kwargs = (
                        self
                        ._get_state_hash('failure', 'Failure in run setup')
                    )
                    l_jobstate.create(**kwargs)
                    failure = True

        if not failure and post_run:
            kwargs = (self
                      ._get_state_hash('post-run', 'Starting post_run setup'))
            post_run_jobstate_id = (
                l_jobstate
                .create(**kwargs).json()['jobstate']['id']
            )
            for cmd in post_run['cmds']:
                self._run_command(cmd, post_run['cwd'], post_run_jobstate_id)
                if rc != 0:
                    kwargs = (
                        self
                        ._get_state_hash('failure', 'Fail in post_run setup')
                    )
                    l_jobstate.create(**kwargs)
                    failure = True

        if not failure:
            kwargs = self._get_state_hash('success', 'Finished running agent')
            l_jobstate.create(**kwargs)
