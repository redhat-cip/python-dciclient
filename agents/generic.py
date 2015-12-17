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

from dciclient.v1.consumers import agent


DCI_LOGIN='admin'
DCI_PASSWORD='admin'
DCI_CS_URL='http://172.17.0.4:5000'
REMOTECI='Boa Lead'
AGENT_HOME='/var/tmp/dci_agent_scripts/'

def get_commands():
    """Define the various pre_run, run and post_run hashes"""
    pre_run = {
        'cwd': '/var/tmp',
        'cmds' : [
            ['bash', '%s/pre_run.sh' % AGENT_HOME],
        ]
    }

    run = {
        'cwd': '/var/tmp',
        'cmds' : [
            ['bash', '%s/run.sh' % AGENT_HOME],
        ]
    }

    post_run = {
        'cwd': '/var/tmp',
        'cmds' : [
            ['bash', '%s/post_run.sh' % AGENT_HOME],
        ]
    }

    return pre_run, run, post_run


if __name__ == '__main__':
    l_agent = agent.Agent(DCI_CS_URL, DCI_LOGIN, DCI_PASSWORD, REMOTECI)

    pre_run, run, post_run = get_commands()
    l_agent.run_agent(run, pre_run, post_run)
