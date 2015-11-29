# Copyright 2015 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from dciclient.v1 import utils
from dciclient.v1.consumers import agent

import os
import six
import shutil
import sys
import tempfile
import yaml

DCI_LOGIN='admin'
DCI_PASSWORD='admin'
DCI_CS_URL='http://127.0.0.1:5000'
REMOTECI='Boa Lead'

venv_dir = tempfile.mkdtemp()
workspace_dir = tempfile.mkdtemp()

def setup_commands(jobinformation):
    """ """
    python_bin = venv_dir + '/bin/python'
    pip_bin = venv_dir + '/bin/pip'
    ansible_playbook_bin = venv_dir + '/bin/ansible-playbook'
    kh_dir = workspace_dir + '/khaleesi'

    cmds = [
        ['virtualenv', venv_dir],
        [pip_bin, 'install', '-U', 'ansible==1.9.2'],
        [ansible_playbook_bin, '--version'],
    ]

    components = jobinformation['components']
    if not isinstance(components, list):
        components = [components]


    for component in components:
    #    if component['componenttype']['name'] != 'git_commit':
    #        continue
        project_canonical_name = component['canonical_project_name']
        component_dir = workspace_dir + '/' + project_canonical_name
        ref = component['ref'] if component['ref'] else ''
        cmds.append(['git', 'init', component_dir])
        cmds.append(['git', 'pull', component['git'], ref]) # cwd: in component_dir
        cmds.append(['git', 'fetch', '--all']) # cwd: in component_dir
        cmds.append(['git', 'clean', '-ffdx']) # cwd: in component_dir
        cmds.append(['git', 'reset', '--hard']) # cwd: in component_dir

        if 'sha' in component:
            cmds.append(['git', 'checkout', '-f', component['sha']]), # cwd: in component_dir

    cmds.append([python_bin, 'setup.py', 'develop']) #cwd: kh_dir/tools/ksgen

    for cmd in cmds:
        print cmd

    return []

def ksgen_command(jobinformation):
    """ """
    ksgen_bin = venv_dir + '/bin/ksgen'
    kh_dir = workspace_dir + '/khaleesi'
    args = []

    structure_from_server = {}
    settings = yaml.load(open(sys.argv[1], 'r'))['test']['data']


    #open(kh_dir + '/ssh.config.ansible', "w").close()
    collected_files_path = ("%s/collected_files" % kh_dir)
    if os.path.exists(collected_files_path):
        shutil.rmtree(collected_files_path)

    cmds = [
        [ksgen_bin, '--config-dir=%s/khaleesi-settings/settings' % ( workspace_dir), 'generate']
    ]

    for ksgen_args in (structure_from_server.get('ksgen_args', {}),
                       settings.get('ksgen_args', {})):
        for k, v in six.iteritems(ksgen_args):
            if isinstance(v, list):
                for sv in v:
                    args.append('--%s' % (k))
                    args.append(sv)
            elif isinstance(v, dict):
                for sv in utils.flatten(v):
                    args.append('--%s' % (k))
                    args.append(sv)
            else:
                args.append('--%s' % (k))
                args.append('%s' % (v))


    args.append('--extra-vars')
    args.append('@' + workspace_dir +
                '/khaleesi-settings/hardware_environments' +
                '/virt/network_configs/none/hw_settings.yml')
    args.append(workspace_dir + '/ksgen_settings.yml')

    environ = os.environ
    environ.update({
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
        'TEST_MACHINE': '', #settings['hypervisor'],
        'PWD': kh_dir,
        'CONFIG_BASE': workspace_dir + '/khaleesi-settings/settings',
        'WORKSPACE': workspace_dir})

    print("test machine is: %s" % environ['TEST_MACHINE'])

    for arg in args:
        cmds[0].append(arg)

    for cmd in cmds:
        print cmd

    return []

def ansible_command(jobinformation):
    """ """
    ansible_playbook_bin = venv_dir + '/bin/ansible-playbook'
    kh_dir = workspace_dir + '/khaleesi'

    #shutil.copyfile(workspace_dir + '/khaleesi/ansible.cfg.example',
    #                workspace_dir + '/khaleesi/ansible.cfg')

    #with open(workspace_dir + '/khaleesi/ansible.cfg', 'a+') as f:
    #    f.write('ssh_args = -F ssh.config.ansible\n')

    #with open(workspace_dir + '/khaleesi/ssh.config.ansible', 'w') as f:
    #    f.write('#nothing\n')
    #    pass

    cmds = [
        [ansible_playbook_bin, '-vvvv', '--extra-vars', '@' + workspace_dir + '/ksgen_settings.yml', '-i', kh_dir + '/local_hosts', kh_dir + '/playbooks/full-job-no-test.yml']
    ]

    for cmd in cmds:
        print cmd

    return []

def get_pre_run_commands(jobinformation):
    return setup_commands(jobinformation) + ksgen_command(jobinformation)

def get_commands(jobinformation):
    """Define the various pre_run, run and post_run hashes"""
    post_run = None

    pre_run = {
        'cwd': '/var/tmp',
        'cmds' : [
            get_pre_run_commands(jobinformation)
        ]
    }

    run = {
        'cwd': '/var/tmp',
        'cmds' : [
            ansible_command(jobinformation)
        ]
    }

    return pre_run, run, post_run


if __name__ == '__main__':
    l_agent = agent.Agent(DCI_CS_URL, DCI_LOGIN, DCI_PASSWORD, REMOTECI)

    pre_run, run, post_run = get_commands(l_agent.jobinformation)
    #l_agent.run_agent(run, pre_run, post_run)
