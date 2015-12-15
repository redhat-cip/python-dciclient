#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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
from dciclient.v1 import utils

DCI_LOGIN = 'admin'
DCI_PASSWORD = 'admin'
DCI_CS_URL = 'http://127.0.0.1:5000'
REMOTECI_ID = '42a71a83-0bae-48c4-886c-d2dba8505163'


class HelloWorld(agent.Agent):
    def __init__(self, remoteci_id):
        session = utils.build_http_session(DCI_CS_URL, DCI_LOGIN, DCI_PASSWORD)
        super(HelloWorld, self).__init__(session=session,
                                         remoteci_id=remoteci_id)

    def pre_run(self):
        return {
            'cwd': '/var/tmp',
            'cmds': [
                ['echo', 'I am in the pre run state.'],
            ]
        }

    def post_run(self):
        return {
            'cwd': '/var/tmp',
            'cmds': [
                ['echo', 'I am in the post run state.'],
            ]
        }

    def run(self):
        return {
            'cwd': '/var/tmp',
            'cmds': [
                ['echo', 'I am in the running state.'],
            ]
        }


if __name__ == '__main__':
    hw_agent = HelloWorld(REMOTECI_ID)
    hw_agent.schedule_job()
    hw_agent.run_agent()
