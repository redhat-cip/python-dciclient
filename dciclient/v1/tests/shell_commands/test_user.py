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


def test_prettytable_output(runner, team_id):
    result = runner.invoke(['user-create', '--name', 'foo',
                            '--password', 'pass', '--role', 'user',
                            '--team_id', team_id])
    user = json.loads(result.output)['user']

    result = runner.invoke(['--format', 'table', 'user-show', '--id',
                            user['id']])

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

    expected_data = (user['id'], user['etag'], user['name'], user['role'],
                     user['team_id'], user['created_at'], user['updated_at'])

    assert header == ('| id | etag | name | role | team_id '
                      '| created_at | updated_at |')

    assert data == '| %s | %s | %s | %s | %s | %s | %s |' % expected_data


def test_create(runner, team_id):
    result = runner.invoke(['user-create', '--name', 'foo',
                            '--password', 'pass', '--role', 'user',
                            '--team_id', team_id])
    user = json.loads(result.output)['user']
    assert user['name'] == 'foo'
    assert user['role'] == 'user'
    assert user['team_id'] == team_id


def test_list(runner, team_id):
    runner.invoke(['user-create', '--name', 'foo',
                   '--password', 'pass', '--role', 'user',
                   '--team_id', team_id])
    runner.invoke(['user-create', '--name', 'bar',
                   '--password', 'pass', '--role', 'user',
                   '--team_id', team_id])
    result = runner.invoke(['user-list'])
    users = json.loads(result.output)['users']
    # NOTE (spredzy): We put 5 because of the 3 creates plus
    # admin and 2 users provisionned during server test
    assert len(users) == 5


def test_update(runner, team_id):
    result = runner.invoke(['user-create', '--name', 'foo',
                            '--password', 'pass', '--role', 'user',
                            '--team_id', team_id])
    user = json.loads(result.output)['user']

    runner.invoke(['user-update', '--id', user['id'],
                   '--etag', user['etag'], '--name', 'bar',
                   '--role', 'admin'])
    result = runner.invoke(['user-show', '--id', user['id']])
    user = json.loads(result.output)['user']

    assert user['name'] == 'bar'
    assert user['role'] == 'admin'


def test_delete(runner, team_id):
    result = runner.invoke(['user-create', '--name', 'foo',
                            '--password', 'pass', '--role', 'user',
                            '--team_id', team_id])
    user = json.loads(result.output)['user']

    result = runner.invoke(['user-delete', '--id', user['id'],
                            '--etag', user['etag']])
    result = json.loads(result.output)
    assert result['message'] == 'User deleted.'


def test_show(runner, team_id):
    result = runner.invoke(['user-create', '--name', 'foo',
                            '--password', 'pass', '--role', 'user',
                            '--team_id', team_id])
    user = json.loads(result.output)['user']

    result = runner.invoke(['user-show', '--id', user['id']])
    user = json.loads(result.output)['user']

    assert user['name'] == 'foo'
