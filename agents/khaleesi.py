#!/usr/bin/env python
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

from dciclient.v1 import utils
from dciclient.v1.api import component
from dciclient.v1.api import context
from dciclient.v1.api import job
from dciclient.v1.api import jobstate

import os
import sys
import tempfile

import six


venv_dir = tempfile.mkdtemp()
workspace_dir = tempfile.mkdtemp()
kh_dir = workspace_dir + '/khaleesi'


def get_requirements_commands():
    pip_bin = venv_dir + '/bin/pip'
    ansible_playbook_bin = venv_dir + '/bin/ansible-playbook'

    commands = [
        ['yum', '-y', 'install', 'python-virtualenv'],
        ['yum', '-y', 'install',
         'https://www.rdoproject.org/repos/rdo-release.rpm'],
        ['yum', '-y', 'install', 'python-glanceclient'],
        ['yum', '-y', 'install', 'python-neutronclient'],
        ['yum', '-y', 'install', 'python-novaclient'],
        ['easy_install', 'pip'],
        ['virtualenv', venv_dir],
        [pip_bin, 'install', '-U', 'ansible==1.9.2'],
        [ansible_playbook_bin, '--version']
    ]

    return commands


def get_components_commands(jobinformation):
    python_bin = venv_dir + '/bin/python'
    jd_components = jobinformation['components']

    commands = []

    for cmpt in jd_components:
        if cmpt['type'] == component.REPO:
            project_name = component['canonical_project_name']
            repo_path = '/etc/yum.repos.d/%s.repo' % project_name
            commands.append(['wget', '-O', repo_path, component['url']])
        elif cmpt['type'] == component.GIT_COMMIT:
            project_name = component['canonical_project_name']
            component_dir = workspace_dir + '/' + project_name
            ref = component['ref'] or ''
            commands.append(['git', 'init', component_dir])
            commands.append({'cwd': component_dir,
                             'cmd': ['git', 'pull', component['git'], ref]})
            commands.append({'cwd': component_dir,
                             'cmd': ['git', 'fetch', '--all']})
            commands.append({'cwd': component_dir,
                             'cmd': ['git', 'clean', '-ffdx']})
            commands.append({'cwd': component_dir,
                             'cmd': ['git', 'reset', '--hard']})
            sha = component['sha']
            if sha:
                commands.append({'cwd': component_dir,
                                 'cmd': ['git', 'checkout', '-f', sha]})
            if project_name == 'khaleesi':
                commands.append({'cwd': '%s/tools/ksgen' % kh_dir,
                                 'cmd': [python_bin, 'setup.py', 'develop']})

    return commands


def _get_components_kh_args(jobinformation):
    jd_components = jobinformation['components']

    kh_args = {}
    for cmpt in jd_components:
        if 'kh_args' in cmpt['data']:
            kh_args.update(cmpt['data']['kh_args'])

    return kh_args


def get_ksgen_commands(jobinformation):
    ksgen_bin = venv_dir + '/bin/ksgen'
    kh_args = _get_components_kh_args(jobinformation)

    commands = [
        {'cwd': kh_dir, 'cmd': ['touch', 'ssh.config.ansible']},
        {'cwd': kh_dir, 'cmd': ['rm', '-rf', 'collected_files']},
    ]

    ksgen_args = ['--%s=%s' % (k, v) for k, v in six.iteritems(kh_args)]

    # TODO(yassine): Get it from CS
    remote_ci_kh_args = {
        'kh_args': {'provisioner': 'openstack',
                    'provisioner-site': 'DCI',
                    'provisioner-topology': 'virthost',
                    'distro': 'rhel-7.2',
                    'workarounds': 'enabled'}
    }
    for k, v in remote_ci_kh_args['kh_args']:
        ksgen_args.append('--%s=%s' % (k, v))

    # Add extra vars settings
    ksgen_args.append('--extra-vars')
    ksgen_args.append('@' + workspace_dir +
                      '/khaleesi-settings/hardware_environments' +
                      '/virt/network_configs/none/hw_settings.yml')

    ksgen_args.append('--extra-vars')
    ksgen_args.append('@' + workspace_dir +
                      '/khaleesi-settings/settings/product/rhos' +
                      '/private_settings/redhat_internal.yml')

    ksgen_args.append(kh_dir + '/ksgen_settings.yml')

    os.environ.update({
        'PYTHONPATH': './tools/ksgen',
        'JOB_NAME': '',
        'ANSIBLE_HOST_KEY_CHECKING': 'False',
        'ANSIBLE_ROLES_PATH': kh_dir + '/roles',
        'ANSIBLE_LIBRARY': kh_dir + '/library',
        'ANSIBLE_DISPLAY_SKIPPED_HOSTS': 'False',
        'ANSIBLE_FORCE_COLOR': 'yes',
        'ANSIBLE_CALLBACK_PLUGINS': kh_dir + '/khaleesi/plugins/callbacks/',
        'ANSIBLE_FILTER_PLUGINS': kh_dir + '/khaleesi/plugins/filters/',
        'ANSIBLE_SSH_ARGS': ' -F ssh.config.ansible',
        'ANSIBLE_TIMEOUT': '60',
        'TEST_MACHINE': 'my.example.com', #settings['hypervisor'],
        'PWD': kh_dir,
        'CONFIG_BASE': workspace_dir + '/khaleesi-settings/settings',
        'WORKSPACE': workspace_dir})

    commands.append({'cwd': kh_dir,
                     'cmd': [ksgen_bin, '--config-dir', 'settings',
                             'generate'] + ksgen_args})
    return commands


def get_ansible_commands():
    ansible_playbook_bin = venv_dir + '/bin/ansible-playbook'

    commands = [
        ['cp', '%s/khaleesi/ansible.cfg.example' % workspace_dir, '%s/khaleesi/ansible.cfg' % workspace_dir],
        ['echo', 'ssh_args = -F ssh.config.ansible', '>>', '%s/khaleesi/ansible.cfg' % workspace_dir],
        ['sed', '-i', 's/control_path/#control_path/g', '%s/khaleesi/ansible.cfg' % workspace_dir],
        {'cwd': kh_dir,
         'cmd': [ansible_playbook_bin, '-vvvv',
                 '--extra-vars', '@%s/ksgen_settings.yml' % kh_dir, '-i',
                 '%s/local_hosts' % kh_dir,
                 '%s/playbooks/full-job-no-test.yml' % kh_dir]}
    ]

    return commands


def retrieve_jobinformation(dci_context, remoteci_id):
    """Retrieve job information"""
    scheduled_job = job.schedule(dci_context, remoteci_id)
    if scheduled_job.status_code != 201:
        print("No job scheduled: '%s'" % scheduled_job.json())
        sys.exit(0)

    scheduled_job_id = scheduled_job.json()['job']['id']
    full_data = job.get_full_data(dci_context, scheduled_job_id)

    return scheduled_job_id, full_data


if __name__ == '__main__':
    dci_context = context.build_dci_context()
    new_job_id, jobinformation = retrieve_jobinformation(dci_context,
                                                         "remoteci_id")

    # 1. Create the pre-run state
    running_state = jobstate.create(dci_context, 'pre-run',
                                    'installing requirements and '
                                    'generate khaleesi playbook', new_job_id,
                                    'team_id')
    pre_run_state_id = running_state['id']

    # 2. Install requirements packages and tools.
    requirements_commands = get_requirements_commands()
    utils.run_commands(dci_context, requirements_commands, '/var/tmp',
                       pre_run_state_id, new_job_id, "team_id")

    # 3. Compute the components of the job
    components_commands = get_components_commands(jobinformation)
    utils.run_commands(dci_context, components_commands, '/var/tmp',
                       pre_run_state_id, new_job_id, "team_id")

    # 4. Compute ksgen
    ksgen_commands = get_ksgen_commands(jobinformation)
    utils.run_commands(dci_context, ksgen_commands, '/var/tmp',
                       pre_run_state_id, new_job_id, "team_id")

    # 5. Create the running state
    running_state = jobstate.create(dci_context, 'running',
                                    'Running khaleesi ansible playbook',
                                    new_job_id, 'team_id')
    running_state_id = running_state['id']

    ansible_commands = get_ansible_commands()
    utils.run_commands(dci_context, ansible_commands, '/var/tmp',
                       running_state_id, new_job_id, "team_id")

    # If we are there, then all the commands have succeed, create success state
    jobstate.create(dci_context, 'success', 'Khaleesi run successfully',
                    new_job_id, 'team_id')
