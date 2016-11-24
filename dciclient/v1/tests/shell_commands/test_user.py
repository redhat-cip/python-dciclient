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


def test_prettytable_output(runner, team_id):
    user = runner.invoke_raw_parse([
        'user-create', '--name', 'foo',
        '--password', 'pass', '--role', 'user',
        '--team_id', team_id])
    assert user['team_id'] == team_id
    assert user == runner.invoke_raw_parse(['user-show', user['id']])


def test_create(runner, team_id):
    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass', '--role', 'user',
                          '--team_id', team_id])['user']
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
    users = runner.invoke(['user-list'])['users']
    # NOTE (spredzy): We put 5 because of the 3 creates plus
    # admin and 2 users provisionned during server test
    assert len(users) == 5


def test_update(runner, team_id):
    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass', '--role', 'user',
                          '--team_id', team_id])['user']

    runner.invoke(['user-update', user['id'],
                   '--etag', user['etag'], '--name', 'bar',
                   '--role', 'admin'])
    user = runner.invoke(['user-show', user['id']])['user']

    assert user['name'] == 'bar'
    assert user['role'] == 'admin'


def test_delete(runner, team_id):
    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass', '--role', 'user',
                          '--team_id', team_id])['user']

    result = runner.invoke(['user-delete', user['id'],
                            '--etag', user['etag']])
    assert result['message'] == 'User deleted.'


def test_show(runner, team_id):
    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass', '--role', 'user',
                          '--team_id', team_id])['user']

    user = runner.invoke(['user-show', user['id']])['user']

    assert user['name'] == 'foo'
