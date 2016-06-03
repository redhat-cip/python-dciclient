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


def test_prettytable_output(runner):
    result = runner.invoke(['team-create', '--name', 'foo'])
    team = json.loads(result.output)['team']

    result = runner.invoke(['--format', 'table', 'team-show', '--id',
                            team['id']])

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

    expected_data = (team['id'], team['name'], team['etag'],
                     team['created_at'], team['updated_at'])

    assert header == '| id | name | etag | created_at | updated_at |'

    assert data == '| %s | %s | %s | %s | %s |' % expected_data


def test_list(runner):
    runner.invoke(['team-create', '--name', 'foo'])
    runner.invoke(['team-create', '--name', 'bar'])
    result = runner.invoke(['team-list'])
    teams = json.loads(result.output)['teams']
    # NOTE (spredzy): We put 4 because of the 2 creates plus
    # admin and user provisionned during server test
    assert len(teams) == 4


def test_create(runner):
    result = runner.invoke(['team-create', '--name', 'foo'])
    team = json.loads(result.output)['team']
    assert team['name'] == 'foo'


def test_update(runner):
    result = runner.invoke(['team-create', '--name', 'foo'])
    team = json.loads(result.output)['team']

    result = runner.invoke(['team-update', '--id', team['id'],
                            '--etag', team['etag'], '--name', 'bar'])
    result = json.loads(result.output)

    assert result['message'] == 'Team updated.'
    assert result['id'] == team['id']


def test_delete(runner):
    result = runner.invoke(['team-create', '--name', 'foo'])
    team = json.loads(result.output)['team']

    result = runner.invoke(['team-delete', '--id', team['id'],
                            '--etag', team['etag']])
    result = json.loads(result.output)

    assert result['message'] == 'Team deleted.'


def test_show(runner):
    result = runner.invoke(['team-create', '--name', 'foo'])
    team = json.loads(result.output)['team']

    result = runner.invoke(['team-show', '--id', team['id']])
    team = json.loads(result.output)['team']

    assert team['name'] == 'foo'
