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

import dciclient.v1.api.jobdefinition as dci_jobdefinition
import dciclient.v1.api.remoteci as dci_remoteci
import dciclient.v1.tripleo_helper as th
from tripleohelper.undercloud import Undercloud

import mock


def test_run_tests(dci_context, job_id):
    remoteci = dci_remoteci.get(dci_context, 'tname').json()['remoteci']
    Undercloud.load_private_key = mock.Mock()
    Undercloud.run = mock.Mock(return_value=('', 0,))
    Undercloud.enable_user = mock.Mock()
    Undercloud.create_stack_user = mock.Mock()
    Undercloud.add_environment_file = mock.Mock()
    th.push_stack_details = mock.Mock()

    th.run_tests(dci_context, '1.2.3.4', 'id_rsa.pub', remoteci['id'])
    print(dci_jobdefinition.list().json())
    assert False
