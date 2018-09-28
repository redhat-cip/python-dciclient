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

from dciclient.v1.api import component
from dciclient.v1.api import job
from dciclient.v1.api import topic


def test_job_create_as_remoteci(dci_context, dci_context_remoteci,
                                components_ids, topic_id, team_user_id):
    topic.attach_team(dci_context, topic_id, team_user_id)

    j = job.create(
        dci_context_remoteci,
        topic_id=topic_id,
        team_id=team_user_id,
        components=components_ids).json()
    assert j['job']['id']


def test_job_put(dci_context, job_id):
    new_comment = 'foo'
    j = job.get(dci_context, job_id).json()['job']
    assert j['comment'] is None
    job.update(dci_context, id=job_id, etag=j['etag'], comment=new_comment)
    r = job.get(dci_context, job_id)
    j = r.json()['job']
    assert j['comment'] == new_comment


def test_job_update(dci_context, job_id):
    r = job.job_update(dci_context, job_id=job_id)
    assert r.status_code == 201
    assert r.json()['job']['update_previous_job_id'] == job_id


def test_job_upgraded(dci_context, job_id, topic_id):
    old = topic.get(dci_context, id=topic_id).json()['topic']
    new = topic.create(dci_context, 'bar_topic', ['type_1'])
    t = new.json()['topic']
    component.create(dci_context, 'bar_component', 'type_1', t['id'])
    topic.update(dci_context, id=topic_id, etag=old['etag'],
                 next_topic_id=t['id'])
    r = job.upgrade(dci_context, job_id=job_id)
    assert r.status_code == 201
    assert r.json()['job']['previous_job_id'] == job_id
