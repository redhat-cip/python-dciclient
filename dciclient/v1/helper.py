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

from dciclient.v1.api import component
from dciclient.v1.api import file
from dciclient.v1.api import job
from dciclient.v1.api import jobdefinition
from dciclient.v1.api import jobstate
from dciclient.v1.api import test

import fcntl
import mimetypes
import os
import select
import subprocess
import traceback

import six
import sys

import tripleohelper.undercloud


def get_test_id(dci_context, name, topic_id):
    print("Use test '%s'" % name)
    test.create(dci_context, name, topic_id)
    return test.get(dci_context, name).json()['test']['id']


def create_jobdefinition(dci_context, components, test_ids,
                         topic_id, jobdef_name=None):
    # If at least one component doesn't exist in the database then a new
    # jobdefinition must be created.
    at_least_one = False
    component_ids = []
    names = []
    for cmpt in components:
        names.append(cmpt['name'])
        created_cmpt = component.create(dci_context, **cmpt)
        if created_cmpt.status_code == 201:
            at_least_one = True
        elif created_cmpt.status_code == 422:
            created_cmpt = component.get(dci_context, cmpt['name'])
        created_cmpt_name = created_cmpt.json()['component']['name']
        component_ids.append(created_cmpt.json()['component']['id'])

    if at_least_one:
        if jobdef_name is None:
            jobdef_name = created_cmpt_name
        jobdef = jobdefinition.create(dci_context, jobdef_name, topic_id)
        if jobdef.status_code == 201:
            jobdef_id = jobdef.json()['jobdefinition']['id']
            for cmpt_id in component_ids:
                jobdefinition.add_component(dci_context, jobdef_id, cmpt_id)
            for test_id in test_ids:
                jobdefinition.add_test(dci_context, jobdef_id, test_id)
            print("Jobdefinition '%s' created." % jobdef_name)
        else:
            print("Error on jobdefinition creation: '%s'", jobdef.json())
    else:
        print("No jobdefinition created.")


def upload_file(context, path, job_id, mime=None):

    if not mime:
        mime = mimetypes.guess_type(path)[0]

    l_file = file.create(context, name=path, content=open(path, 'r').read(),
                         mime=mime, job_id=job_id)

    return l_file


def run_command(context, cmd, cwd, jobstate_id, team_id):
    """This function execute a command and send its log which will be
    attached to a jobstate.
    """
    output = six.StringIO()
    print('* Processing command: %s' % cmd)
    print('* Working directory: %s' % cwd)
    pipe_process = subprocess.Popen(cmd, cwd=cwd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

    fcntl.fcntl(pipe_process.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
    inputs = [pipe_process.stdout]
    outputs = []

    while True:
        readable, writable, exceptional = select.select(inputs, outputs,
                                                        inputs, 60)
        if not readable:
            break
        pstdout = pipe_process.stdout.read().decode('UTF-8', 'ignore')
        if len(pstdout) == 0:
            break
        else:
            print(pstdout)
            output.write(pstdout)

    pipe_process.wait()

    file.create(context, name='_'.join(cmd), content=output.getvalue(),
                mime='text/plain', jobstate_id=jobstate_id)
    output.close()
    return pipe_process.returncode


def run_commands(context, cmds, cwd, jobstate_id, job_id, team_id):
    for cmd in cmds:
        if isinstance(cmd, dict):
            rc = run_command(context, cmd['cmd'], cmd['cwd'], jobstate_id,
                             team_id)
        else:
            rc = run_command(context, cmd, cwd, jobstate_id, team_id)

        if rc != 0:
            error_msg = "Failed on command %s" % cmd
            jobstate.create(context, "failure", error_msg, job_id)
            print(error_msg)
            sys.exit(1)


def run_tests(context, undercloud_ip, key_filename):
    undercloud = tripleohelper.undercloud.Undercloud(
        hostname=undercloud_ip,
        user='root',
        key_filename='/root/.ssh/id_rsa')
    undercloud.create_stack_user()

    j = job.get(context, context.last_job_id).json()['job']
    tests = jobdefinition.get_tests(
        context, j['jobdefinition_id']).json()
    try:
        for t in tests['tests']:
            if 'url' not in t['data']:
                continue
            url = t['data']['url']
            undercloud.add_environment_file(
                user='stack',
                filename='overcloudrc')
            undercloud.run('curl -O ' + url, user='stack')
            undercloud.run('bash -x run.sh', user='stack')
            result = undercloud.run(
                'cat result.xml',
                success_status=(0, 1,),
                user='stack')[0]
            file.create(
                context,
                'result.xml',
                result, mime='application/junit',
                job_id=context.last_job_id)
    except Exception:
        msg = traceback.format_exc()
        print(msg)
        jobstate.create(context,
                        'failure',
                        msg,
                        context.last_job_id)
    else:
        jobstate.create(context, 'success', '', context.last_job_id)
