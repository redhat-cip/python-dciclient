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


def test_prettytable_output(runner):
    team = runner.invoke_raw_parse([
        'team-create',
        '--name', 'foo'])
    assert team['name'] == 'foo'
    assert team == runner.invoke_raw_parse([
        'team-show', team['id']])


def test_list(runner):
    runner.invoke(['team-create', '--name', 'foo'])
    runner.invoke(['team-create', '--name', 'bar'])
    teams = runner.invoke(['team-list'])['teams']
    # NOTE (spredzy): We put 4 because of the 2 creates plus
    # admin and user provisionned during server test
    assert len(teams) == 5


def test_create(runner, team_admin_id):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    assert team['name'] == 'foo'
    assert team['parent_id'] == team_admin_id


def test_create_with_parent_id(runner, team_admin_id, team_id):
    team = runner.invoke(['team-create', '--name', 'foo',
                          '--parent-id', team_id])['team']
    assert team['name'] == 'foo'
    assert team['parent_id'] == team_id


def test_create_with_country_and_email(runner):
    team = runner.invoke(['team-create', '--name', 'foo',
                          '--country', 'FR'])['team']
    assert team['name'] == 'foo'
    assert team['country'] == 'FR'


def test_create_inactive(runner):
    team = runner.invoke(['team-create', '--name', 'foo',
                          '--no-active'])['team']
    assert team['state'] == 'inactive'


def test_create_fail_unauthorized_user_admin(runner_user_admin):
    team = runner_user_admin.invoke(['team-create', '--name', 'foo'])
    assert team['status_code'] == 401


def test_create_fail_unauthorized_user(runner_user):
    team = runner_user.invoke(['team-create', '--name', 'foo'])
    assert team['status_code'] == 401


def test_update(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']

    result = runner.invoke(['team-update', team['id'],
                            '--etag', team['etag'], '--name', 'bar',
                            '--country', 'JP'])

    assert result['team']['id'] == team['id']
    assert result['team']['name'] == 'bar'
    assert result['team']['country'] == 'JP'


def test_update_active(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    assert team['state'] == 'active'

    result = runner.invoke(['team-update', team['id'],
                            '--etag', team['etag'], '--no-active'])

    assert result['team']['id'] == team['id']
    assert result['team']['state'] == 'inactive'

    result = runner.invoke(['team-update', team['id'],
                            '--etag', result['team']['etag'],
                            '--name', 'foobar'])

    assert result['team']['id'] == team['id']
    assert result['team']['state'] == 'inactive'

    result = runner.invoke(['team-update', team['id'],
                            '--etag', result['team']['etag'],
                            '--active'])

    assert result['team']['state'] == 'active'


def test_update_team_external(runner, runner_product_owner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    runner.invoke(['team-update', team['id'],
                   '--etag', team['etag'], '--no-external'])
    team = runner.invoke(['team-show', team['id']])['team']

    assert team['external'] is False


def test_delete(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']

    result = runner.invoke(['team-delete', team['id'],
                            '--etag', team['etag']])

    assert result['message'] == 'Team deleted.'


def test_show(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']

    team = runner.invoke(['team-show', team['id']])['team']

    assert team['name'] == 'foo'


def test_where_on_list(runner):
    runner.invoke(['team-create', '--name', 'foobar42'])

    assert runner.invoke(['team-list', '--where',
                          'name:foobar42'])['_meta']['count'] == 1
