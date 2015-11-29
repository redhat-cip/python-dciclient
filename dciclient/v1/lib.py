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

from dciclient.v1.handlers import componenttype
from dciclient.v1.handlers import file
from dciclient.v1.handlers import job
from dciclient.v1.handlers import jobdefinition
from dciclient.v1.handlers import jobstate
from dciclient.v1.handlers import test
from dciclient.v1.handlers import remoteci

import fcntl
import os
import requests
import subprocess
import tempfile
import time

def get_http_session(dci_cs_url, login, password):
    session = requests.Session()
    session.headers.setdefault('Content-Type', 'application/json')
    session.auth = (login, password)
    session.dci_cs_url = dci_cs_url
    return session


def ensure_componenttype(session, componenttypes):
    """Ensure componenttype exist"""
    componenttype_ids = []

    for ct_name in componenttypes:
        l_componenttype = componenttype.ComponentType(session)
        #try:
        componenttype_ids.append(l_componenttype.create(name=ct_name).json()['componenttype']['id'])
        #except AlreadyExist:
        #    componenttype_ids.append(l_componenttype.show(name=ct_name).json()['id'])
        #    pass
        #except Exception e:
        #    raise e

    return componenttype_ids


def ensure_test(session, tests):
    """Ensure test exist"""
    test_ids = []

    for t_name in tests:
        l_test = test.Test(session)
        #try:
        test_ids.append(l_test.create(name=t_name).json()['test']['id'])
        #except AlreadyExist:
        #    test_ids.append(l_test.show(name=t_name).json()['id'])
        #    pass
        #except Exception e:
        #    raise e

    return test_ids


def create_jobdefinition(session, name, component, test):
    """Create an entry in JobDefinition"""
    l_jobdefinition = jobdefinition.JobDefinition(session)

    jobdefinition_id = l_jobdefinition.create(
        name=name,
        test_id=test,
    ).json()['jobdefinition']['id']

    l_jobdefinition.add_component(
        id=jobdefinition_id,
        component_id=component,
    )


def retrieve_remoteciid(session, remoteci_name):
    """Retrieve a remoteci id by its name"""
    l_remoteci = remoteci.RemoteCI(session)
    remotecis = l_remoteci.list().json()['remotecis']

    for rci in remotecis:
        if remoteci_name == rci['name']:
            remoteci_id = rci['id']
            break

    return remoteci_id


def retrieve_jobinformation(session, remoteci_id, team_id):
    """Retrieve job informations"""
    #embed = ['jobdefinition', 'jobdefinition.components', 'jobdefinition.components.componenttype']
    embed = ['jobdefinition']

    l_job = job.Job(session)
    job_id = l_job.create(recheck=False, remoteci_id=remoteci_id, team_id=team_id).json()['job']['id']

    result = l_job.get(id=job_id, embed=','.join(embed)).json()
    print result
    return result


def _get_state_hash(job_id, status, comment, team_id):
    return  {"job_id": job_id,
             "status": status,
             "comment": comment,
             "team_id": team_id}


def _run_command(session, cmd, cwd, jobstate_id, team_id):
    """ """
    l_file = file.File(session)
    #with open("/var/tmp/thisisatest.log","a+") as stdout:
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
    print f
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
                            team_id=team_id)
    f.close()

    return p.returncode


def run_agent(session, team_id, pre_run, run, post_run=None):
    """Run the agent business logic"""
    l_jobstate = jobstate.JobState(session)

    kwargs = _get_state_hash(run['job_id'], 'Initializing', 'Starting pre_run setup', team_id)
    jobstate_id = l_jobstate.create(**kwargs).json()['jobstate']['id']
    for cmd in pre_run['cmds']:
        _run_command(session, cmd, pre_run['cwd'], jobstate_id, team_id)

    kwargs = _get_state_hash(run['job_id'], 'Ongoing', 'Starting run setup', team_id)
    l_jobstate.create(**kwargs)
    for cmd in run['cmds']:
        _run_command(session, cmd, run['cwd'], jobstate_id, team_id)

    if post_run:
        kwargs = _get_state_hash(run['job_id'], 'Ongoing', 'Starting post_run setup', team_id)
        l_jobstate.create(**kwargs)
        for cmd in post_run['cmds']:
            _run_command(session, cmd, post_run['cwd'], jobstate_id, team_id)

    kwargs = _get_state_hash(run['job_id'], 'Success', 'Finished running agent', team_id)
    l_jobstate.create(**kwargs)
