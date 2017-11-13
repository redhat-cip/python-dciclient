# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Red Hat, Inc
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

from dciclient.v1.api import file
from dciclient.v1.api import files_events


def test_files_events_create(dci_context, job_id):

    file_json = file.create(dci_context, 'name1', 'content1',
                            mime='text/plain', job_id=job_id).json()
    file_id = file_json['file']['id']
    f_events = files_events.list(dci_context, 0)
    assert f_events.status_code == 200

    f_events_data = f_events.json()
    assert f_events_data['files'][-1]['event']['file_id'] == file_id
    assert f_events_data['files'][-1]['event']['action'] == 'create'


def test_files_events_delete(dci_context, job_id):

    file_json = file.create(dci_context, 'name1', 'content1',
                            mime='text/plain', job_id=job_id).json()
    file_id = file_json['file']['id']
    file.delete(dci_context, file_id)
    f_events = files_events.list(dci_context, 0)
    assert f_events.status_code == 200

    f_events_data = f_events.json()
    assert f_events_data['files'][-1]['event']['file_id'] == file_id
    assert f_events_data['files'][-1]['event']['action'] == 'delete'


def test_files_events_delete_from_sequence(dci_context, job_id):

    f_events = files_events.list(dci_context, 0).json()
    init_nb_files = len(f_events['files'])

    for i in range(5):
        file.create(dci_context, 'name%s' % i, 'content%s' % i,
                    mime='text/plain', job_id=job_id)
    f_events = files_events.list(dci_context, 0).json()
    assert len(f_events['files']) == (init_nb_files + 5)

    files_events.delete(dci_context, 4)

    f_events = files_events.list(dci_context, 0).json()
    assert len(f_events['files']) == 3
