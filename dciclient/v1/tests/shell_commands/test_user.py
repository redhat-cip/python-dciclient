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


def test_success_create_default_role(runner, team_id):
    roles = runner.invoke(['role-list'])['roles']
    roles_id = {}
    for role in roles:
        roles_id[role['label']] = role['id']

    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass',
                          '--team_id', team_id])['user']
    assert user['name'] == 'foo'
    assert user['role_id'] == roles_id['USER']
    assert user['team_id'] == team_id


def test_success_create_admin_role(runner, team_id):
    roles = runner.invoke(['role-list'])['roles']
    roles_id = {}
    for role in roles:
        roles_id[role['label']] = role['id']

    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass',
                          '--role_id', roles_id['ADMIN'],
                          '--team_id', team_id])['user']
    assert user['name'] == 'foo'
    assert user['role_id'] == roles_id['ADMIN']
    assert user['team_id'] == team_id


def test_success_list(runner, team_id):
    users_number = len(runner.invoke(['user-list'])['users'])

    runner.invoke(['user-create', '--name', 'foo',
                   '--password', 'pass',
                   '--team_id', team_id])
    runner.invoke(['user-create', '--name', 'bar',
                   '--password', 'pass',
                   '--team_id', team_id])

    users_new_number = len(runner.invoke(['user-list'])['users'])
    assert users_new_number == users_number + 2


def test_success_update(runner, team_id):
    roles = runner.invoke(['role-list'])['roles']
    roles_id = {}
    for role in roles:
        roles_id[role['label']] = role['id']

    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass',
                          '--team_id', team_id])['user']

    runner.invoke(['user-update', user['id'],
                   '--etag', user['etag'], '--name', 'bar',
                   '--role_id', roles_id['ADMIN']])

    user = runner.invoke(['user-show', user['id']])['user']

    assert user['name'] == 'bar'
    assert user['role_id'] == roles_id['ADMIN']


def test_success_delete(runner, team_id):
    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass',
                          '--team_id', team_id])['user']

    result = runner.invoke(['user-delete', user['id'],
                            '--etag', user['etag']])
    assert result['message'] == 'User deleted.'

    result = runner.invoke(['user-show', user['id']])

    assert result['status_code'] == 404


def test_success_show(runner, team_id):
    user = runner.invoke(['user-create', '--name', 'foo',
                          '--password', 'pass',
                          '--team_id', team_id])['user']

    user = runner.invoke(['user-show', user['id']])['user']

    assert user['name'] == 'foo'
