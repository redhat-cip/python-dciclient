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
import json


def test_prettytable_output(runner, topic_id):
    result = runner.invoke(['jobdefinition-create', '--name', 'foo',
                            '--topic_id', topic_id])
    jobdefinition = json.loads(result.output)['jobdefinition']

    result = runner.invoke(['--format', 'table', 'jobdefinition-show', '--id',
                            jobdefinition['id']])

    output = result.output.split('\n')
    # NOTE(spredzy) : The expected output for a table format looks like the
    #                 following :
    #
    # +------------
    # |  id | name
    # +------------
    # | id1 | name1
    # | id2 | name2
    # | id3 | name3
    # +------------
    #
    # The header variable below represents the header data, when more than one
    # space is located between the string and the '|' space number is shrink to
    # one ( this is what ' '.join(string.split()) does
    #
    # The data variable below represents the actual data, when more than one
    # space is located between the string and the '|' space number is shrink to
    # one ( this is what ' '.join(string.split()) does
    header = ' '.join(output[1].split())
    data = ' '.join(output[3].split())

    expected_data = (jobdefinition['id'], jobdefinition['name'],
                     jobdefinition['priority'], jobdefinition['active'],
                     jobdefinition['comment'], jobdefinition['etag'],
                     jobdefinition['created_at'], jobdefinition['updated_at'])

    assert header == ('| id | name | priority | active | comment '
                      '| etag | created_at | updated_at |')

    assert data == '| %s | %s | %s | %s | %s | %s | %s | %s |' % (
        expected_data
    )


def test_list(runner, topic_id):
    result = runner.invoke(['team-list'])
    teams = json.loads(result.output)['teams']
    team_id = teams[0]['id']

    topic_team = runner.invoke(['topic-attach-team', '--id', topic_id,
                                '--team_id', team_id])
    topic_team = json.loads(topic_team.output)

    runner.invoke(['jobdefinition-create', '--name', 'foo', '--topic_id',
                  topic_id])
    runner.invoke(['jobdefinition-create', '--name', 'bar', '--topic_id',
                  topic_id])

    result = runner.invoke(['jobdefinition-list', '--topic_id', topic_id])
    jobdefinitions = json.loads(result.output)['jobdefinitions']

    assert len(jobdefinitions) == 2
    assert jobdefinitions[0]['name'] == 'foo'
    assert jobdefinitions[1]['name'] == 'bar'


def test_create(runner, topic_id):
    result = runner.invoke(['jobdefinition-create', '--name', 'foo',
                            '--topic_id', topic_id])

    jobdefinition = json.loads(result.output)['jobdefinition']
    assert jobdefinition['name'] == 'foo'


def test_delete(runner, topic_id):
    result = runner.invoke(['jobdefinition-create', '--name', 'foo',
                            '--topic_id', topic_id])
    jobdefinition = json.loads(result.output)['jobdefinition']

    result = runner.invoke(['jobdefinition-delete', '--id',
                            jobdefinition['id'], '--etag',
                            jobdefinition['etag']])
    result = json.loads(result.output)

    assert result['message'] == 'Job Definition deleted.'


def test_show(runner, topic_id):
    result = runner.invoke(['jobdefinition-create', '--name', 'foo',
                            '--topic_id', topic_id])
    jobdefinition = json.loads(result.output)['jobdefinition']

    result = runner.invoke(['jobdefinition-show', '--id', jobdefinition['id']])
    jobdefinition = json.loads(result.output)['jobdefinition']

    assert jobdefinition['name'] == 'foo'


def test_annotate(runner, topic_id):
    result = runner.invoke(['jobdefinition-create', '--name', 'foo',
                            '--topic_id', topic_id])

    jd = json.loads(result.output)['jobdefinition']
    result = runner.invoke(['jobdefinition-annotate', '--id', jd['id'],
                            '--comment', 'This is my annotation', '--etag',
                            jd['etag']])

    result = json.loads(result.output)
    assert result['message'] == 'Job Definition updated.'

    result = runner.invoke(['jobdefinition-show', '--id', jd['id']])
    jobdefinition_comm = json.loads(result.output)['jobdefinition']['comment']
    assert jobdefinition_comm == 'This is my annotation'


def test_active(runner, topic_id):
    result = runner.invoke(['jobdefinition-create', '--name', 'foo',
                            '--topic_id', topic_id])

    jd = json.loads(result.output)['jobdefinition']
    result = runner.invoke(['jobdefinition-set-active', '--active', 'False',
                            '--id', jd['id'], '--etag', jd['etag']])

    result = json.loads(result.output)
    assert result['message'] == 'Job Definition updated.'
    result = runner.invoke(['jobdefinition-show', '--id', jd['id']])
    jobdefinition_active = json.loads(result.output)['jobdefinition']['active']
    assert jobdefinition_active is False
