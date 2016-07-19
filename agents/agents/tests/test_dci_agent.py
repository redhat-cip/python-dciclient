# -*- encoding: utf-8 -*-
#
# Copyright 2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import agents.agents.dci_agent as agent
from dciclient.v1.api import jobstate as dci_jobstate
import dciclient.v1.helper
import tripleohelper.undercloud

import mock
import os.path


def test_dci_agent(monkeypatch, dci_context, topic_id, job_id):
    def return_context(**args):
        print(dci_context)
        print(dci_context.dci_cs_api)
        return dci_context
    run_commands = mock.Mock()
    monkeypatch.setattr(agent, 'get_dci_context', return_context)
    monkeypatch.setattr(dciclient.v1.helper, 'run_command', run_commands)
    monkeypatch.setattr(tripleohelper.undercloud, 'Undercloud', mock.Mock())
    monkeypatch.setattr(dciclient.v1.tripleo_helper, 'run_tests', mock.Mock())
    agent.main(['--topic', 'foo_topic', '--config',
                os.path.dirname(__file__) + '/dci_agent.yaml'])

    calls = [
        mock.call(dci_context, [
            'rsync', '-av', '--hard-links',
            'rsync@rhos-mirror.distributed-ci.io:/var/www/htmlpath1/',
            '/var/www/htmlpath1']),
        mock.call(dci_context, [
            'rsync', '-av', '--hard-links',
            'rsync@rhos-mirror.distributed-ci.io:/var/www/htmlsomewhere2/',
            '/var/www/htmlsomewhere2']),
        mock.call(dci_context, 'ansible-playbook provisioning.yaml',
                  shell=True),
        mock.call(dci_context, 'ansible-playbook undercloud.yaml',
                  shell=True),
        mock.call(dci_context, 'ansible-playbook overcloud.yaml',
                  shell=True),
    ]
    run_commands.assert_has_calls(calls)
    from pprint import pprint
    pprint(dci_jobstate.list(dci_context).json()['jobstates'])
    js = dci_jobstate.list(dci_context).json()['jobstates']
    comments = [i['comment'] for i in js]
    assert comments[0] == 'refreshing local mirror'
    assert comments[1] == 'director node provisioning'
    assert comments[2] == 'undercloud deployment'
    assert comments[3] == 'overcloud deployment'
