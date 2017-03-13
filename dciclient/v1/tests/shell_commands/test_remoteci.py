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

from dciclient.v1.api import remoteci
from dciclient.v1.api import team


def test_prettytable_output(runner):
    team = runner.invoke_raw_parse([
        'team-create',
        '--name', 'foo'])
    assert team['name'] == 'foo'
    assert team == runner.invoke_raw_parse([
        'team-show', team['id']])


def test_list(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    runner.invoke(['remoteci-create', '--name', 'foo', '--team_id',
                   team['id']])
    runner.invoke(['remoteci-create', '--name', 'bar', '--team_id',
                   team['id']])
    remotecis = runner.invoke(['remoteci-list'])['remotecis']

    assert len(remotecis) == 2
    assert remotecis[0]['name'] == 'bar'
    assert remotecis[1]['name'] == 'foo'


def test_create(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    remoteci = runner.invoke([
        'remoteci-create', '--name', 'foo', '--team_id',
        team['id'], '--active'])['remoteci']
    assert remoteci['name'] == 'foo'
    assert remoteci['state'] == 'active'


def test_update(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    remoteci = runner.invoke([
        'remoteci-create', '--name', 'foo', '--team_id',
        team['id']])['remoteci']
    result = runner.invoke(['remoteci-update', remoteci['id'],
                            '--etag', remoteci['etag'], '--name', 'bar',
                            '--no-active'])

    assert result['message'] == 'Remote CI updated.'
    assert result['id'] == remoteci['id']


def test_delete(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']

    remoteci = runner.invoke([
        'remoteci-create', '--name', 'foo', '--team_id',
        team['id']])['remoteci']

    result = runner.invoke(['remoteci-delete', remoteci['id'],
                            '--etag', remoteci['etag']])

    assert result['message'] == 'Remote CI deleted.'


def test_show(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    remoteci = runner.invoke([
        'remoteci-create', '--name', 'foo', '--team_id',
        team['id']])['remoteci']

    remoteci = runner.invoke(['remoteci-show', remoteci['id']])['remoteci']

    assert remoteci['name'] == 'foo'


def test_get_data(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    remoteci = runner.invoke([
        'remoteci-create', '--name', 'foo', '--team_id',
        team['id']])['remoteci']

    result = runner.invoke(['remoteci-get-data', remoteci['id']])
    assert result == {}
    runner.invoke(['remoteci-update', remoteci['id'],
                   '--etag', remoteci['etag'], '--data', '{"foo": "bar"}'])
    result = runner.invoke(['remoteci-get-data', remoteci['id']])
    assert result == {'foo': 'bar'}


def test_get_data_missing_key(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    remoteci = runner.invoke([
        'remoteci-create', '--name', 'foo', '--team_id',
        team['id']])['remoteci']

    result = runner.invoke(['remoteci-get-data',
                            remoteci['id'],
                            '--keys', 'missing'])
    assert result == {}


def test_embed(dci_context):
    team_id = team.create(dci_context, name='teama').json()['team']['id']

    rci = remoteci.create(dci_context, name='boa', team_id=team_id).json()
    rci_id = rci['remoteci']['id']

    rci_with_embed = remoteci.get(dci_context,
                                  id=rci_id, embed='team').json()
    embed_team_id = rci_with_embed['remoteci']['team']['id']

    assert team_id == embed_team_id


def test_test(runner, test_id):
    team = runner.invoke(['team-create', '--name', 'osp'])['team']
    remoteci = runner.invoke([
        'remoteci-create', '--name', 'foo', '--team_id',
        team['id'], '--active'])['remoteci']
    result = runner.invoke(['remoteci-attach-test',
                            remoteci['id'], '--test_id', test_id])
    tests = runner.invoke(['remoteci-list-test',
                           remoteci['id']])['tests']
    assert len(tests) == 1
    result = runner.invoke(['remoteci-unattach-test',
                            remoteci['id'], '--test_id', test_id])
    print(result)
    tests = runner.invoke(['remoteci-list-test',
                           remoteci['id']])['tests']
    assert len(tests) == 0
