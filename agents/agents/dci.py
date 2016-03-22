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

import platform
import sys

DCI_INFRA_URL = 'http://softwarefactory-project.io/r/dci-infra'


def _get_os_version():
    current_platform = platform.linux_distribution()

    if current_platform[0] == 'Fedora':
        current_os = 'f%s' % current_platform[1]
    elif current_platform[0] in ['CentOS Linux',
                                 'Red Hat Enterprise Linux Server']:
        current_os = 'el%s' % current_platform[1][:1]

    return current_os


def get_pre_run_commands(component_details, environment_url):

    current_os = _get_os_version()
    cmpnt = component_details['components'][0]

    commands = [
        ['rm', '-rf', '/var/tmp/dci-infra'],
        ['sudo', 'rm', '/etc/yum.repos.d/dci.repo'],
        ['sudo', 'curl', '-o', '/etc/yum.repos.d/dci.repo', '%s/dci%s.repo' %
            (cmpnt['url'],
             current_os)],
        ['git', 'clone', DCI_INFRA_URL],
    ]

    commands.append({'cwd': '/var/tmp/dci-infra',
                     'cmd': ['git', 'clone', environment_url, 'data']})

    return commands


def get_running_commands():

    commands = []

    commands.append({'cwd': '/var/tmp/dci-infra',
                     'cmd': ['ansible-galaxy', 'install', '-r',
                             'installed_roles', '-p', 'roles/']})
    commands.append({'cwd': '/var/tmp/dci-infra',
                     'cmd': ['ansible-playbook', '-i', 'data/hosts',
                             'playbook.yml', '--tags', 'dci-core']})

    return commands


def get_post_run_commands():

    commands = []

    commands.append({'cwd': '/var/tmp/dci-infra',
                     'cmd': ['rake', 'serverspec:functional']})

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
        remoteci_id, team_id, topic_id, environment_url = args
    except ValueError:
        print('dci-agent-dci remoteci_id team_id topic_id environment_url')
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
    pre_run_commands = get_pre_run_commands(jobinformation, environment_url)
    helper.run_commands(dci_context, pre_run_commands, '/var/tmp',
                        pre_run_state_id, new_job_id, team_id)

    # 3. Create the running state
    running_state = jobstate.create(dci_context, 'running',
                                    'Running commands',
                                    new_job_id).json()
    running_state_id = running_state['jobstate']['id']

    # 4. Run the ansible deployment
    running_commands = get_running_commands()
    helper.run_commands(dci_context, running_commands, '/var/tmp',
                        running_state_id, new_job_id, team_id)

    # 5. Create the post-run state
    post_run_state = jobstate.create(dci_context,
                                     'post-run',
                                     'Running post-run commands',
                                     new_job_id) .json()
    post_run_state_id = post_run_state['jobstate']['id']

    # 6. Run the test suite
    post_run_commands = get_post_run_commands()
    helper.run_commands(dci_context, post_run_commands, '/var/tmp',
                        post_run_state_id, new_job_id, team_id)

    # If we are there, then all the commands have succeed, create success state
    jobstate.create(dci_context, 'success', 'Rake commands run successfully',
                    new_job_id)

if __name__ == '__main__':
    main()
