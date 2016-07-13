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

import dciclient.v1.api.file as dci_file
import dciclient.v1.helper as dci_helper


def test_run_command(dci_context, jobstate_id):
    dci_helper.run_command(
        dci_context,
        ['bash', '-c', 'for i in $(seq 1 3); do echo "ga bu zo me"; done'],
        jobstate_id=jobstate_id)
    new_file = dci_file.list(dci_context).json()['files'][1]
    assert new_file['size'] == 36
    assert 'ga bu zo me' in new_file['name']
