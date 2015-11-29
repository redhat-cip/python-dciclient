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


    def retrieve_jobinformation(self):
        """Retrieve job informations"""
        #embed = ['jobdefinition', 'jobdefinition.components', 'jobdefinition.components.componenttype']
        embed = ['jobdefinition']

        l_job = job.Job(self._s)
        job_id = l_job.create(recheck=False, remoteci_id=self.remoteci_id, team_id=self.team_id).json()['job']['id']

        result = l_job.get(id=job_id, embed=','.join(embed)).json()
        return result


    def _get_state_hash(self, job_id, status, comment):
        return  {"job_id": job_id,
                 "status": status,
                 "comment": comment,
                 "team_id": self.team_id}


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

    def run_agent(self, pre_run, run, post_run=None):
        """Run the agent business logic"""
        l_jobstate = jobstate.JobState(self._s)

        kwargs = self._get_state_hash(run['job_id'], 'Initializing', 'Starting pre_run setup')
        jobstate_id = l_jobstate.create(**kwargs).json()['jobstate']['id']
        for cmd in pre_run['cmds']:
            self._run_command(cmd, pre_run['cwd'], jobstate_id)

        kwargs = self._get_state_hash(run['job_id'], 'Ongoing', 'Starting run setup')
        l_jobstate.create(**kwargs)
        for cmd in run['cmds']:
            self._run_command(cmd, run['cwd'], jobstate_id)

        if post_run:
            kwargs = self._get_state_hash(run['job_id'], 'Ongoing', 'Starting post_run setup')
            l_jobstate.create(**kwargs)
            for cmd in post_run['cmds']:
                self._run_command(cmd, post_run['cwd'], jobstate_id)

        kwargs = self._get_state_hash(run['job_id'], 'Success', 'Finished running agent')
        l_jobstate.create(**kwargs)
