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

from dciclient.v1.api import component
from dciclient.v1.api import file
from dciclient.v1.api import jobdefinition
from dciclient.v1.api import jobstate
from dciclient.v1.api import test

import fcntl
import mimetypes
import os
import subprocess

import six
import sys
import time


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


def run_command(context, cmd, cwd=None, jobstate_id=None, team_id=None,
                shell=False, expected_retcodes=[0]):
    """This function execute a command and send its log which will be
    attached to a jobstate.
    """
    if not jobstate_id:
        jobstate_id = context.last_jobstate_id
    output = six.StringIO()
    print('* Processing command: %s' % cmd)
    if cmd:
        print('* Working directory: %s' % cwd)
    pipe_process = subprocess.Popen(cmd, cwd=cwd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    shell=shell)

    fcntl.fcntl(pipe_process.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
    name = cmd if shell else u'_'.join(cmd)

    def flush_buffer(output):
        if output.tell() == 0:
            return
        to_send = output.getvalue()
        file.create(
            context, name=name.encode('utf-8'),
            content=to_send.encode('utf-8'),
            mime='text/plain',
            jobstate_id=jobstate_id)
        output.seek(0)
        output.truncate()

    p_status = None
    while p_status is None:
        time.sleep(0.5)
        try:
            p_status = pipe_process.poll()
            pstdout = pipe_process.stdout.read().decode('UTF-8', 'ignore')
        except IOError:
            pass
        else:
            if len(pstdout) > 0:
                output.write(pstdout)
            if output.tell() > 2048:
                flush_buffer(output)

    pipe_process.wait()
    flush_buffer(output)

    if pipe_process.returncode not in expected_retcodes:
        raise DCIExecutionError()


def run_commands(context, cmds, cwd, jobstate_id, job_id, team_id):
    for cmd in cmds:
        try:
            if isinstance(cmd, dict):
                run_command(context, cmd['cmd'], cmd['cwd'], jobstate_id,
                            team_id)
            else:
                run_command(context, cmd, cwd, jobstate_id, team_id)
        except DCIExecutionError:
            error_msg = "Failed on command %s" % cmd
            jobstate.create(context, "failure", error_msg, job_id)
            sys.exit(1)


class DCIExecutionError(Exception):
    """DCI command excution failure."""
    pass
