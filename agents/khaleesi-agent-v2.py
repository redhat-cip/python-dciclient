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
import requests
import six
import shutil
import sys
import tempfile
import yaml

DCI_LOGIN='admin'
DCI_PASSWORD='admin'
DCI_CS_URL='http://dci.enovance.com'
REMOTECI='BoaCorp'

venv_dir = tempfile.mkdtemp()
workspace_dir = tempfile.mkdtemp()
kh_dir = workspace_dir + '/khaleesi'

def setup_commands(jobinformation):
    """ """
    python_bin = venv_dir + '/bin/python'
    pip_bin = venv_dir + '/bin/pip'
    ansible_playbook_bin = venv_dir + '/bin/ansible-playbook'

    cmds = [
        ['yum', '-y', 'install', 'python-virtualenv'],
        ['easy_install', 'pip'],
        ['virtualenv', venv_dir],
        [pip_bin, 'install', '-U', 'ansible==1.9.2'],
        [ansible_playbook_bin, '--version'],
        ['cp', '-r', '/vagrant/dci/khaleesi', workspace_dir],
        ['cp', '-r', '/vagrant/dci/khaleesi-settings', workspace_dir],
    ]

    components = jobinformation['components']
    if not isinstance(components, list):
        components = [components]


    #for component in components:
        #if component['componenttype']['name'] == 'repo':
        #    continue
        #if component['componenttype']['name'] == 'git_commit':
        #    continue
    #    if 'osp' in component['canonical_project_name']:
    #        cmds.append(['wget', '-O', '/etc/yum.repos.d/%s.repo' % component['canonical_project_name'], component['url']])

    #    elif 'khaleesi' in component['canonical_project_name']:
    #        project_canonical_name = component['canonical_project_name']
    #        component_dir = workspace_dir + '/' + project_canonical_name
    #        ref = component['ref'] if component['ref'] else ''
    #        cmds.append(['git', 'init', component_dir])
    #        cmds.append([{'cwd': component_dir}, 'git', 'pull', component['git'], ref])
    #        cmds.append([{'cwd': component_dir}, 'git', 'fetch', '--all'])
    #        cmds.append([{'cwd': component_dir}, 'git', 'clean', '-ffdx'])
    #        cmds.append([{'cwd': component_dir}, 'git', 'reset', '--hard'])

    #        if 'sha' in component:
    #            cmds.append([{'cwd': component_dir}, 'git', 'checkout', '-f', component['sha']]),

    cmds.append([{'cwd': '%s/tools/ksgen' % kh_dir}, python_bin, 'setup.py', 'develop'])

    return cmds

def ksgen_command(jobinformation):
    """ """
    ksgen_bin = venv_dir + '/bin/ksgen'
    args = []

    # TODO(spredzy): Re-enable when backend handle merge of data fields
    #structure_from_server = {}
    #settings = yaml.load(open(sys.argv[1], 'r'))['test']['data']

    cmds = [
        [{'cwd': kh_dir}, 'touch', 'ssh.config.ansible'],
        [{'cwd': kh_dir}, 'rm', '-rf', 'collected_files'],
        [{'cwd': kh_dir}, ksgen_bin, '--config-dir', 'settings', 'generate']
    ]

    # TODO(spredzy): Re-enable when backend handle merge of data fields
    #for ksgen_args in (structure_from_server.get('ksgen_args', {}),
    #                   settings.get('ksgen_args', {})):
    #    for k, v in six.iteritems(ksgen_args):
    #        if isinstance(v, list):
    #            for sv in v:
    #                args.append('--%s' % (k))
    #                args.append(sv)
    #        elif isinstance(v, dict):
    #            for sv in utils.flatten(v):
    #                args.append('--%s' % (k))
    #                args.append(sv)
    #        else:
    #            args.append('--%s' % (k))
    #            args.append('%s' % (v))

    tmp_args = "--provisioner=openstack \
                --provisioner-site=DCI \
                --provisioner-topology=virthost \
                --installer=rdo_manager \
                --installer-env=virthost \
                --installer-images=import \
                --installer-network=neutron \
                --installer-network-isolation=none \
                --installer-network-variant=ml2-vxlan \
                --installer-post_action=default \
                --installer-topology=minimal_no_ceph \
                --installer-tempest=smoke \
                --installer-updates=none \
                --distro=rhel-7.2 \
                --product=rhos \
                --product-repo=puddle \
                --product-version-build=latest \
                --product-version=8_director \
                --workarounds=enabled \
                --extra-vars=product.build=latest \
                --extra-vars=product.repo.puddle_pin_version=2015-12-03.2 \
                --extra-vars=product.repo.puddle_director_pin_version=2015-12-03.1"

    args = args + tmp_args.split()

    args.append('--extra-vars')
    args.append('@' + workspace_dir +
                '/khaleesi-settings/hardware_environments' +
                '/virt/network_configs/none/hw_settings.yml')

    args.append('--extra-vars')
    args.append('@' + workspace_dir +
                '/khaleesi-settings/settings/product/rhos' +
                '/private_settings/redhat_internal.yml')

    args.append(kh_dir + '/ksgen_settings.yml')

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
        'TEST_MACHINE': 'my.example.com', #settings['hypervisor'],
        'PWD': kh_dir,
        'CONFIG_BASE': workspace_dir + '/khaleesi-settings/settings',
        'WORKSPACE': workspace_dir})

    for arg in args:
        cmds[2].append(arg)

    return cmds

def ansible_command(jobinformation):
    """ """
    ansible_playbook_bin = venv_dir + '/bin/ansible-playbook'

    cmds = [
        ['cp', '%s/khaleesi/ansible.cfg.example' % workspace_dir, '%s/khaleesi/ansible.cfg' % workspace_dir],
        ['echo', 'ssh_args = -F ssh.config.ansible', '>>', '%s/khaleesi/ansible.cfg' % workspace_dir],
        ['sed', '-i', 's/control_path/#control_path/g', '%s/khaleesi/ansible.cfg' % workspace_dir],
        [{'cwd': kh_dir}, ansible_playbook_bin, '-vvvv', '--extra-vars', '@%s/ksgen_settings.yml' % kh_dir, '-i', '%s/local_hosts' % kh_dir, '%s/playbooks/full-job-no-test.yml' % kh_dir]
    ]

    return cmds

def get_pre_run_commands(jobinformation):
    return setup_commands(jobinformation) + ksgen_command(jobinformation)

def get_commands(jobinformation):
    """Define the various pre_run, run and post_run hashes"""
    post_run = None

    pre_run = {
        'cwd': '/var/tmp',
        'cmds' : get_pre_run_commands(jobinformation)
    }

    run = {
        'cwd': '/var/tmp',
        'cmds' : ansible_command(jobinformation)
    }

    return pre_run, run, post_run


if __name__ == '__main__':
    l_agent = agent.Agent(DCI_CS_URL, DCI_LOGIN, DCI_PASSWORD, REMOTECI)
    pre_run, run, post_run = get_commands(l_agent.jobinformation)
    l_agent.run_agent(run, pre_run, post_run)
