# -*- encoding: utf-8 -*-
#
# Copyright 2015-2016 Red Hat, Inc.
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

from dciclient.v1.api import job

import json


def test_get_full_data(job_id, dci_context):
    full_data_job = job.get_full_data(dci_context, job_id)
    assert full_data_job['remoteci']['data'] == {'remoteci': 'remoteci'}
    assert full_data_job['jobdefinition']['name'] == 'tname'
    assert full_data_job['components'][0]['name'] == 'hihi'


def test_list(runner, dci_context, remoteci_id):
    topic = runner.invoke(['topic-create', '--name', 'osp'])
    topic = json.loads(topic.output)['topic']

    result = runner.invoke(['team-list'])
    teams = json.loads(result.output)['teams']
    team_id = teams[0]['id']

    topic_team = runner.invoke(['topic-attach-team', '--id', topic['id'],
                                '--team_id', team_id])
    topic_team = json.loads(topic_team.output)

    jd = runner.invoke(['jobdefinition-create', '--name', 'foo', '--topic_id',
                       topic['id'], '--component_types', 'foobar'])
    jd = json.loads(jd.output)['jobdefinition']

    component = runner.invoke(['component-create', '--name', 'foo',
                               '--type', 'foobar', '--topic_id', topic['id']])
    component = json.loads(component.output)['component']

    job.schedule(dci_context, remoteci_id, topic['id'])
    l_job = runner.invoke(['job-list'])
    l_job = json.loads(l_job.output)
    assert len(l_job['jobs']) == 1
    assert l_job['jobs'][0]['remoteci_id'] == remoteci_id
    assert l_job['jobs'][0]['jobdefinition_id'] == jd['id']


def test_delete(runner, job_id):
    l_job = runner.invoke(['job-show', '--id', job_id])
    l_job_etag = json.loads(l_job.output)['job']['etag']

    result = runner.invoke(['job-delete', '--id', job_id,
                            '--etag', l_job_etag])
    result = json.loads(result.output)

    assert result['message'] == 'Job deleted.'


def test_recheck(runner, job_id):
    result = runner.invoke(['job-recheck', '--id', job_id])
    result = json.loads(result.output)['job']

    assert result['status'] == 'new'


def test_results(runner, job_id):
    result = runner.invoke(['job-results', '--id', job_id])
    result = json.loads(result.output)['results'][0]

    assert result['filename'] == 'res_junit.xml'


def test_attach_issue(runner, job_id):
    result = runner.invoke(['job-list-issue', '--id', job_id])
    result = json.loads(result.output)['_meta']['count']
    assert result == 0

    runner.invoke(
        ['job-attach-issue', '--id', job_id, '--url',
         'https://github.com/redhat-cip/dci-control-server/issues/2']
    )
    result = runner.invoke(['job-list-issue', '--id', job_id])
    result = json.loads(result.output)['_meta']['count']
    assert result == 1


def test_unattach_issue(runner, job_id):
    result = runner.invoke(['job-list-issue', '--id', job_id])
    result = json.loads(result.output)['_meta']['count']
    assert result == 0

    runner.invoke(
        ['job-attach-issue', '--id', job_id, '--url',
         'https://github.com/redhat-cip/dci-control-server/issues/2']
    )
    result = runner.invoke(['job-list-issue', '--id', job_id])
    res = json.loads(result.output)['_meta']['count']
    issue_id = json.loads(result.output)['issues'][0]['id']
    assert res == 1

    runner.invoke(
        ['job-unattach-issue', '--id', job_id, '--issue_id', issue_id]
    )
    result = runner.invoke(['job-list-issue', '--id', job_id])
    result = json.loads(result.output)['_meta']['count']
    assert result == 0
