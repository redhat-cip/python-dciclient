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

from __future__ import unicode_literals


def test_prettytable_output(runner, topic_id):
    jobdefinition = runner.invoke_raw_parse([
        'jobdefinition-create',
        '--name', 'foo',
        '--topic_id', topic_id])
    assert jobdefinition == runner.invoke_raw_parse([
        'jobdefinition-show', jobdefinition['id']])


def test_list(runner, topic_id):
    teams = runner.invoke(['team-list'])['teams']
    team_id = teams[0]['id']

    runner.invoke(['topic-attach-team', topic_id,
                   '--team_id', team_id])

    runner.invoke(['jobdefinition-create', '--name', 'foo', '--topic_id',
                  topic_id])
    runner.invoke(['jobdefinition-create', '--name', 'bar', '--topic_id',
                  topic_id])

    jobdefinitions = runner.invoke([
        'jobdefinition-list',
        '--topic_id', topic_id])['jobdefinitions']

    assert len(jobdefinitions) == 2
    assert jobdefinitions[0]['name'] == 'bar'
    assert jobdefinitions[1]['name'] == 'foo'


def test_create(runner, topic_id):
    jobdefinition = runner.invoke([
        'jobdefinition-create', '--name', 'foo',
        '--topic_id', topic_id])['jobdefinition']
    assert jobdefinition['name'] == 'foo'


def test_delete(runner, topic_id):
    jobdefinition = runner.invoke([
        'jobdefinition-create', '--name', 'foo',
        '--topic_id', topic_id])['jobdefinition']

    result = runner.invoke(['jobdefinition-delete',
                            jobdefinition['id'], '--etag',
                            jobdefinition['etag']])
    assert result['message'] == 'Job Definition deleted.'


def test_update(runner, topic_id):
    jd = jobdefinition = runner.invoke([
        'jobdefinition-create', '--name', 'foo',
        '--topic_id', topic_id])['jobdefinition']

    jobdefinition = runner.invoke([
        'jobdefinition-show', jd['id']])['jobdefinition']
    assert jobdefinition['name'] == 'foo'
    assert jobdefinition['priority'] == 0

    result = runner.invoke([
        'jobdefinition-update', jd['id'],
        '--etag', jd['etag'], '--name', 'bar',
        '--priority', 10])

    assert result['message'] == 'Job Definition updated.'

    jobdefinition = runner.invoke([
        'jobdefinition-show', jd['id']])['jobdefinition']
    assert jobdefinition['name'] == 'bar'
    assert jobdefinition['priority'] == 10


def test_show(runner, topic_id):
    jobdefinition = runner.invoke([
        'jobdefinition-create', '--name', 'foo',
        '--topic_id', topic_id])['jobdefinition']

    jobdefinition = runner.invoke([
        'jobdefinition-show',
        jobdefinition['id']])['jobdefinition']

    assert jobdefinition['name'] == 'foo'


def test_annotate(runner, topic_id):
    jd = runner.invoke([
        'jobdefinition-create', '--name', 'foo',
        '--topic_id', topic_id])['jobdefinition']
    result = runner.invoke(['jobdefinition-annotate', jd['id'],
                            '--comment', 'This is my annotation', '--etag',
                            jd['etag']])
    assert result['message'] == 'Job Definition updated.'

    result = runner.invoke(['jobdefinition-show', jd['id']])
    jobdefinition_comm = result['jobdefinition']['comment']
    assert jobdefinition_comm == 'This is my annotation'


def test_active(runner, topic_id):
    jd = runner.invoke(['jobdefinition-create', '--name', 'foo',
                        '--topic_id', topic_id])['jobdefinition']

    result = runner.invoke(['jobdefinition-set-active', '--no-active',
                            jd['id'], '--etag', jd['etag']])

    assert result['message'] == 'Job Definition updated.'
    jobdefinition_active = runner.invoke([
        'jobdefinition-show',
        jd['id']])['jobdefinition']['state']
    assert jobdefinition_active == 'inactive'


def test_test(runner, topic_id, test_id):
    jd = runner.invoke(['jobdefinition-create', '--name', 'foo',
                        '--topic_id', topic_id])['jobdefinition']

    result = runner.invoke(['jobdefinition-attach-test',
                            jd['id'], '--test_id', test_id])
    tests = runner.invoke(['jobdefinition-list-test',
                           jd['id']])['tests']
    assert len(tests) == 1
    result = runner.invoke(['jobdefinition-unattach-test',
                            jd['id'], '--test_id', test_id])
    print(result)
    tests = runner.invoke(['jobdefinition-list-test',
                           jd['id']])['tests']
    assert len(tests) == 0
