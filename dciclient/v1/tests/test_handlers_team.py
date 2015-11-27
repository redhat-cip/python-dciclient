# -*- encoding: utf-8 -*-
#
# Copyright 2015 Red Hat, Inc.
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
    header = ' '.join(output[1].split())
    data = ' '.join(output[3].split())

    assert header == "| id | name | etag | created_at | updated_at |"
    assert data == "| %s | %s | %s | %s | %s |" % (
        team['id'], team['name'], team['etag'], team['created_at'],
        team['updated_at'])


def test_list(runner):
    runner.invoke(['team-create', '--name', 'foo'])
    runner.invoke(['team-create', '--name', 'bar'])
    result = runner.invoke(['team-list'])
    teams = json.loads(result.output)['teams']
    # NOTE (spredzy): We put 5 because of the 2 creates plus
    # admin, company_a and company_b provisionned during server
    # test
    assert len(teams) == 5
    assert teams[3]['name'] == 'foo'
    assert teams[4]['name'] == 'bar'


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
    assert result['name'] == 'bar'


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
