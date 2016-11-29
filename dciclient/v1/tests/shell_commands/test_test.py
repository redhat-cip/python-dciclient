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
    team = runner.invoke_raw_parse(['team-create', 'osp'])
    assert team['name'] == 'osp'
    assert team == runner.invoke_raw_parse([
        'team-show', team['id']])


def test_list(runner):
    team = runner.invoke(['team-create', 'osp'])['team']
    assert team['name'] == 'osp'

    teams = runner.invoke(['team-list'])['teams']
    team_id = teams[0]['id']

    runner.invoke(['test-create', 'foo', '--team_id', team_id])
    runner.invoke(['test-create', 'bar', '--team_id', team_id])
    tests = runner.invoke(['test-list', '--team_id', team_id])['tests']
    assert len(tests) == 2
    assert tests[0]['name'] == 'foo'
    assert tests[1]['name'] == 'bar'
    output = runner.invoke_raw_parse(['test-list', '--team_id', team_id])
    assert output['team_id'] == team_id


def test_create(runner):
    team = runner.invoke(['team-create', 'osp'])['team']
    assert team['name'] == 'osp'

    test = runner.invoke([
        'test-create', 'foo', '--team_id',
        team['id']])['test']
    assert test['name'] == 'foo'


def test_delete(runner):
    team = runner.invoke(['team-create', 'osp'])['team']
    assert team['name'] == 'osp'

    test = runner.invoke(['test-create', 'foo', '--team_id',
                          team['id']])['test']

    result = runner.invoke(['test-delete', test['id']])

    assert result['message'] == 'Test deleted.'


def test_show(runner):
    team = runner.invoke(['team-create', 'osp'])['team']
    assert team['name'] == 'osp'

    test = runner.invoke(['test-create', 'foo', '--team_id',
                          team['id']])['test']

    test = runner.invoke(['test-show', test['id']])['test']

    assert test['name'] == 'foo'
