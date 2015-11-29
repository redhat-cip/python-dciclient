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

from dciclient.v1.handlers import component
from dciclient.v1.handlers import file
from dciclient.v1.handlers import job
from dciclient.v1.handlers import jobdefinition
from dciclient.v1.handlers import jobstate
from dciclient.v1.handlers import remoteci
from dciclient.v1.consumers import dciconsumer

import fcntl
import os
import requests
import subprocess
import tempfile
import time

class Agent(dciconsumer.DCIConsumer):
    """A DCI agent class"""

    def __init__(self, dci_cs_url, login, password, remoteci_name):
        super(Agent, self).__init__(dci_cs_url, login, password)
        self.remoteci_id, self.team_id = self._retrieve_context(remoteci_name)
        self.job_id, self.jobinformation = self._retrieve_jobinformation()


    def _retrieve_context(self, remoteci_name):
        """Retrieve a remoteci id and team_id by the remote_ci name"""
        l_remoteci = remoteci.RemoteCI(self._s)
        remotecis = l_remoteci.list().json()['remotecis']

        for rci in remotecis:
            if remoteci_name == rci['name']:
                remoteci_id = rci['id']
                team_id = rci['team_id']
                break

        return remoteci_id, team_id


    def _retrieve_jobinformation(self):
        """Retrieve job informations"""
        job_embed = ['jobdefinition']
        component_embed = ['componenttype']

        l_job = job.Job(self._s)
        l_jobdefinition = jobdefinition.JobDefinition(self._s)
        l_component = component.Component(self._s)

        job_data = l_job.schedule(remoteci_id=self.remoteci_id).json()['job']
        #job_data = l_job.schedule(recheck=False, remoteci_id=self.remoteci_id, team_id=self.team_id).json()['job']
        jobdefinition_data = l_job.get(id=job_data['id'], embed=','.join(job_embed)).json()['job']['jobdefinition']
        component_data = l_jobdefinition.get_components(jobdefinition_data['id']).json()['components']

        jobinformation = {
            'job': job_data,
            'jobdefinition': jobdefinition_data,
            'components' : component_data,
        }

        return job_data['id'], jobinformation


    def _get_state_hash(self, status, comment):
        return  {'job_id': self.job_id,
                 'status': status,
                 'comment': comment,
                 'team_id': self.team_id}


    def _run_command(self, cmd, cwd, jobstate_id):
        """ """
        l_file = file.File(self._s)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)

        f = tempfile.TemporaryFile()
        begin_at = int(time.time())
        fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        while p.returncode is None:
            try:
                s = p.stdout.read()
                if s:
                    f.write(s)
            except (OSError, IOError, TypeError):
                # ignore exceptions if there is no more data
                pass
            if time.time() - begin_at > 600:
                p.kill()
                break
            p.poll()
            time.sleep(0.1)

        f.flush()
        f.seek(0)
        output = ""
        while True:
            s = f.read(1024).decode('UTF-8', 'ignore')
            output += s
            if s == '':
                break
        file_id = l_file.create(name='_'.join(cmd),
                                content=output,
                                mime='text/plain',
                                jobstate_id=jobstate_id,
                                team_id=self.team_id)
        f.close()

        return p.returncode

    def run_agent(self, run, pre_run=None, post_run=None):
        """Run the agent business logic"""
        l_jobstate = jobstate.JobState(self._s)
        kwargs = self._get_state_hash('initializing', 'Starting run agent')
        jobstate_id = l_jobstate.create(**kwargs).json()['jobstate']['id']

        if pre_run:
            kwargs = self._get_state_hash('initializing', 'Starting pre_run setup')
            pre_run_jobstate_id = l_jobstate.create(**kwargs).json()['jobstate']['id']
            for cmd in pre_run['cmds']:
                self._run_command(cmd, pre_run['cwd'], pre_run_jobstate_id)

        kwargs = self._get_state_hash('ongoing', 'Starting run setup')
        run_jobstate_id = l_jobstate.create(**kwargs).json()['jobstate']['id']
        for cmd in run['cmds']:
            self._run_command(cmd, run['cwd'], run_jobstate_id)

        if post_run:
            kwargs = self._get_state_hash('ongoing', 'Starting post_run setup')
            post_run_jobstate_id = l_jobstate.create(**kwargs).json()['jobstate']['id']
            for cmd in post_run['cmds']:
                self._run_command(cmd, post_run['cwd'], post_run_jobstate_id)

        kwargs = self._get_state_hash('success', 'Finished running agent')
        final_jobstate_id = l_jobstate.create(**kwargs).json()['jobstate']['id']
        # TODO (spredzy) : To remove when the UI will not display only last item
        for cmd in run['cmds']:
            self._run_command(cmd, run['cwd'], final_jobstate_id)
