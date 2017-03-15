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
from dciclient.v1.api import jobdefinition
from dciclient.v1.api import remoteci
from dciclient.v1.api import test

import pytest
import requests
import requests.exceptions


try:
    requests.get('http://google.com')
except requests.exceptions.ConnectionError:
    internet_cnx = False
else:
    internet_cnx = True


def test_get_full_data(job_id, dci_context):
    full_data_job = job.get_full_data(dci_context, job_id)
    assert full_data_job['remoteci']['data'] == {'remoteci': 'remoteci'}
    assert full_data_job['jobdefinition']['name'] == 'tname'
    cpt_names = set([i['name'] for i in full_data_job['components']])
    assert cpt_names == set(['hihi', 'haha'])


def test_list(runner, dci_context, remoteci_id):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']

    teams = runner.invoke(['team-list'])['teams']
    team_id = teams[0]['id']

    runner.invoke(['topic-attach-team', topic['id'], '--team_id', team_id])

    jd = runner.invoke(['jobdefinition-create',
                        '--name', 'foo',
                        '--topic_id', topic['id'],
                        '--component_types', 'foobar'])['jobdefinition']

    runner.invoke(['component-create', '--name', 'foo',
                   '--type', 'foobar', '--topic_id',
                   topic['id']])['component']

    job.schedule(dci_context, remoteci_id, topic['id'])
    l_job = runner.invoke(['job-list'])
    assert len(l_job['jobs']) == 1
    assert l_job['jobs'][0]['remoteci']['id'] == remoteci_id
    assert l_job['jobs'][0]['jobdefinition']['id'] == jd['id']
    output = runner.invoke_raw_parse(['job-list'])
    assert output['jobdefinition/name'] == 'foo'
    assert output['id'] == l_job['jobs'][0]['id']

    l_job = runner.invoke(['job-list', '--where',
                           'remoteci_id:' + remoteci_id])
    assert len(l_job['jobs']) == 1


def test_list_with_limit(runner, job_factory):
    for _ in range(6):
        job_factory()
    # test --limit XX
    l_job = runner.invoke(['job-list'])
    assert len(l_job['jobs']) == 6
    l_job = runner.invoke(['job-list', '--limit', 1])
    assert len(l_job['jobs']) == 1


def test_delete(runner, job_id):
    l_job = runner.invoke(['job-show', job_id])
    l_job_etag = l_job['job']['etag']

    result = runner.invoke(['job-delete', job_id,
                            '--etag', l_job_etag])

    assert result['message'] == 'Job deleted.'


def test_recheck(runner, job_id):
    result = runner.invoke(['job-recheck', job_id])['job']

    assert result['status'] == 'new'


def test_results(runner, job_id):
    result = runner.invoke(['job-results', job_id])['results'][0]

    assert result['filename'] == 'res_junit.xml'


@pytest.mark.skipif(not internet_cnx, reason="internet connection required")
def test_attach_issue(runner, job_id):
    result = runner.invoke(['job-list-issue', job_id])['_meta']['count']
    assert result == 0

    issue = runner.invoke(
        ['job-attach-issue', job_id, '--url',
         'https://github.com/redhat-cip/dci-control-server/issues/2']
    )
    # NOTE(Goneri): until we fix the consistency issue with this endpoint:
    # https://softwarefactory-project.io/r/6863
    if 'issue' in issue:
        issue = issue['issue']
    else:
        issue['id'] = issue['issue_id']
    result = runner.invoke(['job-list-issue', job_id])
    assert issue['id'] == result['issues'][0]['id']


@pytest.mark.skipif(not internet_cnx, reason="internet connection required")
def test_unattach_issue(runner, job_id):
    result = runner.invoke(['job-list-issue', job_id])['_meta']['count']
    assert result == 0

    runner.invoke(
        ['job-attach-issue', job_id, '--url',
         'https://github.com/redhat-cip/dci-control-server/issues/2']
    )
    result = runner.invoke(['job-list-issue', job_id])
    res = result['_meta']['count']
    issue_id = result['issues'][0]['id']
    assert res == 1

    runner.invoke(
        ['job-unattach-issue', job_id, '--issue_id', issue_id]
    )
    result = runner.invoke(['job-list-issue', job_id])
    count = result['_meta']['count']
    assert count == 0


def test_job_output(runner, job_id):
    result = runner.invoke_raw(['job-output', job_id])
    assert result.output.startswith('[pre-run]')


def test_job_list(runner, dci_context, team_id, topic_id,
                  remoteci_id, component_id):
    kwargs = {'name': 'tname', 'topic_id': topic_id,
              'component_types': ['git_review']}
    jd = jobdefinition.create(dci_context, **kwargs).json()
    jobdefinition_id = jd['jobdefinition']['id']

    kwargs = {'name': 'test_jobdefinition', 'team_id': team_id}
    test_id = test.create(dci_context, **kwargs).json()['test']['id']
    jobdefinition.add_test(dci_context, jobdefinition_id, test_id)
    kwargs = {'name': 'test_remoteci', 'team_id': team_id}
    test_id = test.create(dci_context, **kwargs).json()['test']['id']
    remoteci.add_test(dci_context, remoteci_id, test_id)

    job_id = job.schedule(
        dci_context, remoteci_id, topic_id).json()['job']['id']
    result = runner.invoke(['job-list-test', job_id])
    assert len(result['tests']) == 2
    assert result['tests'][0]['name'] == 'test_jobdefinition'
    assert result['tests'][1]['name'] == 'test_remoteci'


def test_metas(runner, job_id):
    result = runner.invoke(['job-list-issue', job_id])['_meta']['count']
    assert result == 0
    meta = runner.invoke(['job-set-meta', job_id, 'foo', 'var'])['meta']
    metas = runner.invoke(['job-list-meta', job_id])['metas']
    assert len(metas) == 1
    assert metas[0]['id'] == meta['id']
    assert metas[0]['value'] == 'var'
    runner.invoke(['job-delete-meta', job_id, meta['id']])
    metas = runner.invoke(['job-list-meta', job_id])['metas']
    assert len(metas) == 0
