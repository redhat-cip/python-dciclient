#!/usr/bin/env python
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

from dciclient.v1.api import context
from dciclient.v1.api import job
from dciclient.v1.api import jobstate
from dciclient.v1 import helper

from optparse import OptionParser

import sys


def get_pre_run_commands():

    commands = []

    return commands


def get_running_commands(component_details):

    cmpnt = component_details['components'][0]

    commands = [
        ['rm', '-rf', cmpnt['canonical_project_name']],
        ['git', 'clone', cmpnt['git']]
    ]

    commands.append({'cwd': '/var/tmp/%s' % cmpnt['canonical_project_name'],
                     'cmd': ['git', 'checkout', cmpnt['sha']]})
    commands.append({'cwd': '/var/tmp/%s' % cmpnt['canonical_project_name'],
                     'cmd': ['tox']})
    return commands


def retrieve_jobinformation(dci_context, remoteci_id, topic_id):
    """Retrieve job information"""
    scheduled_job = job.schedule(dci_context, remoteci_id, topic_id)
    if scheduled_job.status_code != 201:
        print("No job scheduled: '%s'" % scheduled_job.json())
        sys.exit(0)

    scheduled_job_id = scheduled_job.json()['job']['id']
    print("* Job scheduled: %s" % scheduled_job_id)
    full_data = job.get_full_data(dci_context, scheduled_job_id)

    return scheduled_job_id, full_data


def parse_command_line():
    parser = OptionParser("")
    parser.add_option("-u", "--dci-login", dest="dci_login",
                      help="DCI login")
    parser.add_option("-p", "--dci-password", dest="dci_password",
                      help="DCI password")
    parser.add_option("-a", "--dci-cs-url", dest="dci_cs_url",
                      help="DCI CS url")

    return parser.parse_args()


def main():
    (options, args) = parse_command_line()

    try:
        remoteci_id, team_id, topic_id = args
    except ValueError:
        print('dci-agent-tox remoteci_id team_id topic_id')
        sys.exit(1)

    dci_context = context.build_dci_context(options.dci_cs_url,
                                            options.dci_login,
                                            options.dci_password)

    new_job_id, jobinformation = retrieve_jobinformation(dci_context,
                                                         remoteci_id,
                                                         topic_id)

    # 1. Create the pre-run state
    pre_run_state = jobstate.create(dci_context,
                                    'pre-run',
                                    'Running pre-run commands',
                                    new_job_id) .json()
    pre_run_state_id = pre_run_state['jobstate']['id']

    # 2. Install requirements packages and tools.
    pre_run_commands = get_pre_run_commands()
    helper.run_commands(dci_context, pre_run_commands, '/var/tmp',
                        pre_run_state_id, new_job_id, team_id)

    # 5. Create the running state
    running_state = jobstate.create(dci_context, 'running',
                                    'Running commands',
                                    new_job_id).json()
    running_state_id = running_state['jobstate']['id']

    # 6. Run the echo helloworld command
    running_commands = get_running_commands(jobinformation)
    helper.run_commands(dci_context, running_commands, '/var/tmp',
                        running_state_id, new_job_id, team_id)

    # If we are there, then all the commands have succeed, create success state
    jobstate.create(dci_context, 'success', 'Tox commands run successfully',
                    new_job_id)

if __name__ == '__main__':
    main()
