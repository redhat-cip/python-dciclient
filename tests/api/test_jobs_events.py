# -*- coding: utf-8 -*-
#
# Copyright (C) Red Hat, Inc
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

from dciclient.v1.api import jobs_events
from dciclient.v1.api import jobstate


def test_jobs_events_create(dci_context, job_id):

    js = jobstate.create(dci_context, 'success', 'lol', job_id)
    assert js.status_code == 201
    all_je = jobs_events.list(dci_context, 0)
    assert all_je.status_code == 200
    all_je_data = all_je.json()
    assert len(all_je_data['jobs_events']) > 0


def test_jobs_events_delete_from_sequence(dci_context, job_id):

    js = jobstate.create(dci_context, 'success', 'lol', job_id)
    assert js.status_code == 201
    all_je = jobs_events.list(dci_context, 0)
    assert all_je.status_code == 200
    all_je_data = all_je.json()
    assert len(all_je_data['jobs_events']) > 0

    jobs_events.delete(dci_context, 0)

    all_je = jobs_events.list(dci_context, 0)
    assert all_je.status_code == 200
    all_je_data = all_je.json()
    assert len(all_je_data['jobs_events']) == 0


def test_jobs_event_sequence(dci_context):

    je = jobs_events.get_sequence(dci_context)
    assert je.status_code == 200
    je_data = je.json()['sequence']
    assert 'sequence' in je_data
    assert 'etag' in je_data

    je_put = jobs_events.update_sequence(dci_context, je_data['etag'], 1234)
    assert je_put.status_code == 204

    je = jobs_events.get_sequence(dci_context)
    assert je.status_code == 200
    assert je.json()['sequence']['sequence'] == 1234
