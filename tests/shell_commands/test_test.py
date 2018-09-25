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

import dciclient.v1.api as api


def test_prettytable_output(runner):
    team = runner.invoke_raw_parse(['team-create', '--name', 'osp'])
    assert team['name'] == 'osp'
    assert team == runner.invoke_raw_parse([
        'team-show', team['id']])


def test_list(runner):
    team = runner.invoke(['team-create', '--name', 'osp'])['team']
    assert team['name'] == 'osp'

    teams = runner.invoke(['team-list'])['teams']
    team_id = teams[0]['id']

    runner.invoke(['test-create', '--name', 'foo', '--team-id', team_id])
    runner.invoke(['test-create', '--name', 'bar', '--team-id', team_id])
    tests = runner.invoke(['test-list', '--team-id', team_id])['tests']
    assert len(tests) == 2
    assert tests[0]['name'] == 'bar'
    assert tests[1]['name'] == 'foo'
    output = runner.invoke_raw_parse(['test-list', '--team-id', team_id])
    assert output['team_id'] == team_id


def test_create(runner):
    team = runner.invoke(['team-create', '--name', 'osp'])['team']
    assert team['name'] == 'osp'

    test = runner.invoke([
        'test-create', '--name', 'foo', '--team-id',
        team['id']])['test']
    assert test['name'] == 'foo'


def test_create_inactive(runner):
    team = runner.invoke(['team-create', '--name', 'osp'])['team']
    assert team['name'] == 'osp'

    test = runner.invoke([
        'test-create', '--name', 'foo', '--team-id',
        team['id'], '--no-active'])['test']
    assert test['state'] == 'inactive'


def test_create_data(runner):
    team = runner.invoke(['team-create', '--name', 'osp'])['team']
    assert team['name'] == 'osp'

    test = runner.invoke([
        'test-create',
        '--name', 'foo',
        '--team-id', team['id'],
        '--data', '{"Foo": 2}'])['test']
    assert test['name'] == 'foo'


def test_create_bad_data(runner):
    team = runner.invoke(['team-create', '--name', 'osp'])['team']
    assert team['name'] == 'osp'

    r = runner.invoke_raw_parse([
        'test-create', 'foo',
        '--team-id', team['id'],
        '--data', '{Foo: 2}'])
    # TODO(Gonéri): should instead ensure we print the fine message
    assert '"--data": this option expects a valid JSON' in r


def test_update_active(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    test = runner.invoke([
        'test-create',
        '--name', 'foo',
        '--team-id', team['id'],
        '--data', '{"Foo": 2}'])['test']

    assert test['state'] == 'active'

    result = runner.invoke(['test-update', test['id'], '--etag', test['etag'],
                            '--no-active'])

    assert result['test']['id'] == test['id']
    assert result['test']['state'] == 'inactive'

    result = runner.invoke(['test-update', test['id'], '--etag',
                            result['test']['etag'], '--name', 'foobar'])

    assert result['test']['id'] == test['id']
    assert result['test']['state'] == 'inactive'
    assert result['test']['name'] == 'foobar'

    result = runner.invoke(['test-update', test['id'], '--etag',
                            result['test']['etag'], '--active'])

    assert result['test']['state'] == 'active'


def test_delete(runner):
    team = runner.invoke(['team-create', '--name', 'osp'])['team']
    assert team['name'] == 'osp'

    test = runner.invoke(['test-create', '--name', 'foo', '--team-id',
                          team['id']])['test']

    result = runner.invoke(['test-delete', test['id']])

    assert result['message'] == 'Test deleted.'


def test_show(runner):
    team = runner.invoke(['team-create', '--name', 'osp'])['team']
    assert team['name'] == 'osp'

    test = runner.invoke(['test-create', '--name', 'foo', '--team-id',
                          team['id']])['test']

    test = runner.invoke(['test-show', test['id']])['test']

    assert test['name'] == 'foo'


def test_list_user(runner_test_user, dci_context_test_user, test_user_id,
                   team_user_id):
    tests = api.team.list_tests(dci_context_test_user,
                                team_user_id).json()['tests']
    assert len(tests) == 1

    tests = runner_test_user.invoke(['test-list'])['tests']
    assert len(tests) == 1
