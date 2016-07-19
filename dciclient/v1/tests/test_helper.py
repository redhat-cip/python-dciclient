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
        ['echo', 'bob'],
        jobstate_id=jobstate_id)
    # temporary debug print to trace an issue with the gate
    print(dci_file.list(dci_context).json())
    new_file = dci_file.list(dci_context).json()['files'][1]
    assert new_file['size'] == 4
    assert 'bob' in new_file['name']


def test_run_command_shell(dci_context, jobstate_id):
    dci_helper.run_command(
        dci_context,
        'echo foo bar',
        shell=True)
    files = dci_file.list(dci_context).json()['files']
    assert files[1]['name'] == 'echo foo bar'
    f = dci_file.content(dci_context, files[1]['id'])
    assert f.content.decode(encoding='UTF-8') == 'foo bar\n'
