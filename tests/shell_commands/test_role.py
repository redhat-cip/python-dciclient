# -*- encoding: utf-8 -*-
#
# Copyright 2017 Red Hat, Inc.
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


def test_prettytable_output(runner):
    role = runner.invoke_raw_parse([
        'role-create',
        '--name', 'foo'])
    assert role['name'] == 'foo'
    assert role == runner.invoke_raw_parse([
        'role-show', role['id']])
    assert 'etag' not in runner.invoke_raw_parse(['role-list'])
    assert 'etag' in runner.invoke_raw_parse(['role-list', '--long'])


def test_success_create_basic(runner):
    role = runner.invoke(['role-create', '--name', 'myrole'])['role']
    assert role['name'] == 'myrole'


def test_success_create_full(runner):
    role = runner.invoke(['role-create', '--name', 'myrole', '--label',
                          'MYROLE', '--description', 'myrole',
                          '--active'])['role']
    assert role['name'] == 'myrole'
    assert role['label'] == 'MYROLE'
    assert role['description'] == 'myrole'
    assert role['state'] == 'active'


def test_create_inactive(runner, team_id):
    role = runner.invoke(['role-create', '--name', 'myrole',
                          '--no-active'])['role']
    assert role['state'] == 'inactive'


def test_list(runner):
    roles_number = len(runner.invoke(['role-list'])['roles'])

    runner.invoke(['role-create', '--name', 'foo'])
    runner.invoke(['role-create', '--name', 'bar'])

    roles_new_number = len(runner.invoke(['role-list'])['roles'])

    assert roles_new_number == roles_number + 2


def test_fail_create_unauthorized_user_admin(runner_user_admin):
    role = runner_user_admin.invoke(['role-create', '--name', 'foo'])
    assert role['status_code'] == 401


def test_fail_create_unauthorized_user(runner_user):
    role = runner_user.invoke(['role-create', '--name', 'foo'])
    assert role['status_code'] == 401


def test_success_update(runner):
    role = runner.invoke(['role-create', '--name', 'foo', '--description',
                          'foo_desc'])['role']

    result = runner.invoke(['role-update', role['id'],
                            '--etag', role['etag'], '--name', 'bar',
                            '--description', 'bar_desc'])

    assert result['role']['id'] == role['id']
    assert result['role']['name'] == 'bar'
    assert result['role']['description'] == 'bar_desc'


def test_update_active(runner, team_id):
    role = runner.invoke(['role-create', '--name', 'myrole'])['role']
    assert role['state'] == 'active'

    result = runner.invoke(['role-update', role['id'],
                            '--etag', role['etag'], '--no-active'])

    assert result['role']['id'] == role['id']
    assert result['role']['state'] == 'inactive'

    result = runner.invoke(['role-update', role['id'],
                            '--etag', result['role']['etag'],
                            '--name', 'foobar'])

    assert result['role']['state'] == 'inactive'

    result = runner.invoke(['role-update', role['id'],
                            '--etag', result['role']['etag'],
                            '--active'])

    assert result['role']['state'] == 'active'


def test_delete(runner):
    role = runner.invoke(['role-create', '--name', 'foo'])['role']

    result = runner.invoke(['role-delete', role['id'],
                            '--etag', role['etag']])

    assert result['message'] == 'Role deleted.'

    result = runner.invoke(['role-show', role['id']])

    assert result['status_code'] == 404


def test_show(runner):
    role = runner.invoke(['role-create', '--name', 'foo'])['role']

    role = runner.invoke(['role-show', role['id']])['role']

    assert role['name'] == 'foo'
