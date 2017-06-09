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
        '--password', 'pass', '--team_id', team_id])
    assert user['team_id'] == team_id
    assert user == runner.invoke_raw_parse(['user-show', user['id']])
    assert 'etag' not in runner.invoke_raw_parse(['user-list'])
    assert 'etag' in runner.invoke_raw_parse(['user-list', '--long'])


def test_create_user(runner, team_id, role_user):
    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass', '--team_id', team_id])['user']
    assert user['name'] == 'foo'
    assert user['team_id'] == team_id
    assert user['role_id'] == role_user['id']


def test_create_admin(runner, team_id, role_admin):
    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass', '--role_id', role_admin['id'],
                          '--team_id', team_id])['user']
    assert user['name'] == 'foo'
    assert user['team_id'] == team_id
    assert user['role_id'] == role_admin['id']


def test_create_super_admin(runner, team_id, role_super_admin):
    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass', '--role_id',
                          role_super_admin['id'],
                          '--team_id', team_id])['user']
    assert user['name'] == 'foo'
    assert user['team_id'] == team_id
    assert user['role_id'] == role_super_admin['id']


def test_create_inactive(runner, team_id):
    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass',
                          '--team_id', team_id, '--no-active'])['user']
    assert user['state'] == 'inactive'


def test_list(runner, test_user, team_id):
    runner.invoke(['user-create', '--name', 'bar',
                   '--password', 'pass', '--team_id', team_id])
    users = runner.invoke(['user-list'])['users']
    # NOTE (spredzy): We put 5 because of the 3 creates plus
    # admin and 2 users provisionned during server test
    assert len(users) == 5


def test_update(runner, test_user, role_admin, role_user):
    assert test_user['role_id'] == role_user['id']

    runner.invoke(['user-update', test_user['id'],
                   '--etag', test_user['etag'], '--name', 'bar',
                   '--role_id', role_admin['id']])
    user = runner.invoke(['user-show', test_user['id']])['user']

    assert user['name'] == 'bar'
    assert user['role_id'] == role_admin['id']


def test_update_active(runner, test_user, team_id):
    assert test_user['state'] == 'active'

    result = runner.invoke(['user-update', test_user['id'],
                            '--etag', test_user['etag'], '--no-active'])

    assert result['message'] == 'User updated.'
    assert result['id'] == test_user['id']

    user = runner.invoke(['user-show', test_user['id']])['user']

    assert user['state'] == 'inactive'
    result = runner.invoke(['user-update', user['id'],
                            '--etag', user['etag'], '--active'])

    assert result['message'] == 'User updated.'
    user_state = runner.invoke(
        ['user-show', user['id']]
    )['user']['state']

    assert user_state == 'active'


def test_delete(runner, test_user, team_id):
    result = runner.invoke(['user-delete', test_user['id'],
                            '--etag', test_user['etag']])
    assert result['message'] == 'User deleted.'


def test_show(runner, test_user, team_id):
    user = runner.invoke(['user-show', test_user['id']])['user']

    assert user['name'] == test_user['name']


def test_where_on_list(runner, test_user, team_id):
    runner.invoke(['user-create', '--name', 'foo2',
                   '--password', 'pass', '--team_id', team_id])
    runner.invoke(['user-create', '--name', 'foo3', '--password', 'pass',
                   '--team_id', team_id])
    assert runner.invoke(['user-list'])["_meta"]["count"] == 6
    assert runner.invoke(['user-list', '--where',
                          'name:foo'])["_meta"]["count"] == 1
