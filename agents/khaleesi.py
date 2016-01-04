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

from dciclient.v1.api import component
from dciclient.v1.api import context
from dciclient.v1.api import job
from dciclient.v1.api import jobstate
from dciclient.v1 import utils

import sys
import tempfile

import six


workspace_dir = tempfile.mkdtemp()
khaleesi_dir = workspace_dir + '/khaleesi'
ansible_playbook_bin = workspace_dir + '/bin/ansible-playbook'


def get_requirements_commands():
    pip_bin = workspace_dir + '/bin/pip'

    commands = [
        ['yum', '-y', 'install', 'python-virtualenv'],
        ['virtualenv', workspace_dir],
        [pip_bin, 'install', '-U', 'ansible==1.9.2'],
        [ansible_playbook_bin, '--version']
    ]

    return commands


def get_components_commands(jobinformation):
    python_bin = workspace_dir + '/bin/python'
    jd_components = jobinformation['components']

    commands = []

    for cmpt in jd_components:
        if cmpt['type'] == component.GIT_COMMIT:
            project_name = cmpt['canonical_project_name']
            component_dir = workspace_dir + '/' + project_name
            ref = cmpt['ref'] or ''
            commands.append({'cwd': workspace_dir,
                             'cmd': ['git', 'clone', cmpt['git']]})
            if ref:
                commands.append({'cwd': component_dir,
                                 'cmd': ['git', 'checkout', ref]})
            sha = cmpt['sha']
            if sha:
                commands.append({'cwd': component_dir,
                                 'cmd': ['git', 'checkout', '-f', sha]})
            if project_name == 'khaleesi':
                commands.append({'cwd': khaleesi_dir,
                                 'cmd': ['cp', 'ansible.cfg.example',
                                         'ansible.cfg']})
                commands.append({'cwd': '%s/tools/ksgen' % khaleesi_dir,
                                 'cmd': [python_bin, 'setup.py', 'install']})
    return commands


def _get_kh_args_from_components(jobinformation):
    jd_components = jobinformation['components']

    kh_args = {}
    for cmpt in jd_components:
        if (cmpt['type'] == component.KH_INSTALLER or
                cmpt['type'] == component.PUDDLE):
            kh_args.update(cmpt['data']['kh_args'])

    return kh_args


def get_ksgen_commands(jobinformation):
    ksgen_bin = workspace_dir + '/bin/ksgen'
    kh_args = _get_kh_args_from_components(jobinformation)

    commands = [
        {'cwd': khaleesi_dir, 'cmd': ['touch', 'ssh.config.ansible']},
        {'cwd': khaleesi_dir, 'cmd': ['rm', '-rf', 'collected_files']},
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
    for k, v in six.iteritems(remote_ci_kh_args['kh_args']):
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

    ksgen_args.append(khaleesi_dir + '/ksgen_settings.yml')

    commands.append({'cwd': khaleesi_dir,
                     'cmd': [ksgen_bin, '--config-dir', 'settings',
                             'generate'] + ksgen_args})
    return commands


def get_ansible_commands():
    ansible_playbook_bin = workspace_dir + '/bin/ansible-playbook'

    commands = [
        ['cp', '%s/khaleesi/ansible.cfg.example' % workspace_dir,
         '%s/khaleesi/ansible.cfg' % workspace_dir],
        ['echo', 'ssh_args = -F ssh.config.ansible', '>>',
         '%s/khaleesi/ansible.cfg' % workspace_dir],
        ['sed', '-i', 's/control_path/#control_path/g',
         '%s/khaleesi/ansible.cfg' % workspace_dir],
        {'cwd': khaleesi_dir,
         'cmd': [ansible_playbook_bin, '-vvvv',
                 '--extra-vars', '@%s/ksgen_settings.yml' % khaleesi_dir, '-i',
                 '%s/local_hosts' % khaleesi_dir,
                 '%s/playbooks/full-job-no-test.yml' % khaleesi_dir]}
    ]

    return commands


def retrieve_jobinformation(dci_context, remoteci_id):
    """Retrieve job information"""
    scheduled_job = job.schedule(dci_context, remoteci_id)
    if scheduled_job.status_code != 201:
        print("No job scheduled: '%s'" % scheduled_job.json())
        sys.exit(0)

    scheduled_job_id = scheduled_job.json()['job']['id']
    print("* Job scheduled: %s" % scheduled_job_id)
    full_data = job.get_full_data(dci_context, scheduled_job_id)

    return scheduled_job_id, full_data


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("%s remoteci_id team_id" % sys.argv[0])
        sys.exit(1)
    remoteci_id = sys.argv[1]
    team_id = sys.argv[2]

    dci_context = context.build_dci_context()
    new_job_id, jobinformation = retrieve_jobinformation(dci_context,
                                                         remoteci_id)

    # 1. Create the pre-run state
    pre_run_state = jobstate.create(dci_context, 'pre-run',
                                    'installing requirements and '
                                    'generate khaleesi playbook', new_job_id,
                                    team_id).json()
    pre_run_state_id = pre_run_state['jobstate']['id']

    # 2. Install requirements packages and tools.
    requirements_commands = get_requirements_commands()
    utils.run_commands(dci_context, requirements_commands, '/var/tmp',
                       pre_run_state_id, new_job_id, team_id)

    # 3. Compute the components of the job
    components_commands = get_components_commands(jobinformation)
    utils.run_commands(dci_context, components_commands, '/var/tmp',
                       pre_run_state_id, new_job_id, team_id)

    # 4. Compute ksgen
    ksgen_commands = get_ksgen_commands(jobinformation)
    utils.run_commands(dci_context, ksgen_commands, '/var/tmp',
                       pre_run_state_id, new_job_id, team_id)

    # 5. Create the running state
    running_state = jobstate.create(dci_context, 'running',
                                    'Running khaleesi ansible playbook',
                                    new_job_id, team_id).json()
    running_state_id = running_state['jobstate']['id']

    # 6. Run the Khaleesi Ansible playbook
    ansible_commands = get_ansible_commands()
    utils.run_commands(dci_context, ansible_commands, '/var/tmp',
                       running_state_id, new_job_id, team_id)

    # If we are there, then all the commands have succeed, create success state
    jobstate.create(dci_context, 'success', 'Khaleesi run successfully',
                    new_job_id, team_id)
