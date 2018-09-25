# -*- encoding: utf-8 -*-
#
# Copyright Red Hat, Inc.
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


def test_create(runner, job_id):
    analytic = runner.invoke(['analytic-create',
                              '--job-id', job_id,
                              '--name', 'bug1',
                              '--type', 'infrastructure',
                              '--url', 'http://bugzilla/1',
                              '--data', '{"root_cause": {}}'])['analytic']
    assert analytic['name'] == 'bug1'
    assert analytic['job_id'] == job_id
    assert analytic['type'] == 'infrastructure'
    assert analytic['url'] == 'http://bugzilla/1'
    assert analytic['data'] == {'root_cause': {}}


def test_show(runner, job_id):
    analytic = runner.invoke(['analytic-create',
                              '--job-id', job_id,
                              '--name', 'bug1',
                              '--type', 'infrastructure',
                              '--url', 'http://bugzilla/1',
                              '--data', '{"root_cause": {}}'])['analytic']
    assert analytic['name'] == 'bug1'

    analytic = runner.invoke(['analytic-show',
                              '--job-id', job_id,
                              analytic['id']])['analytic']
    assert analytic['name'] == 'bug1'
    assert analytic['type'] == 'infrastructure'
    assert analytic['url'] == 'http://bugzilla/1'
    assert analytic['data'] == {'root_cause': {}}


def test_list(runner, job_id):
    analytic = runner.invoke(['analytic-create',
                              '--job-id', job_id,
                              '--name', 'bug1',
                              '--type', 'infrastructure',
                              '--url', 'http://bugzilla/1',
                              '--data', '{"root_cause": {}}'])['analytic']
    assert analytic['name'] == 'bug1'

    analytic = runner.invoke(['analytic-create',
                              '--job-id', job_id,
                              '--name', 'bug2',
                              '--type', 'infrastructure',
                              '--url', 'http://bugzilla/2',
                              '--data', '{"root_cause": {}}'])['analytic']
    assert analytic['name'] == 'bug2'

    all_anc = runner.invoke(['analytic-list',
                             '--job-id', job_id])
    assert len(all_anc['analytics']) == 2


def test_update(runner, job_id, dci_context):
    analytic = runner.invoke(['analytic-create',
                              '--job-id', job_id,
                              '--name', 'bug1',
                              '--type', 'infrastructure',
                              '--url', 'http://bugzilla/1',
                              '--data', '{"root_cause": {}}'])['analytic']
    assert analytic['name'] == 'bug1'

    analytic = runner.invoke(['analytic-update',
                              analytic['id'],
                              '--job-id', job_id,
                              '--name', 'bug2',
                              '--type', 'infrastructure',
                              '--url', 'http://bugzilla/2',
                              '--data', '{"root_cause": {}}'])['analytic']
    assert analytic['name'] == 'bug2'
    assert analytic['url'] == 'http://bugzilla/2'


def test_delete(runner, job_id):
    pass
