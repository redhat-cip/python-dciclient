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


def test_list(runner):
    result = runner.invoke(['team-create', '--name', 'foo'])
    team = json.loads(result.output)['team']

    runner.invoke(['remoteci-create', '--name', 'foo', '--team_id',
                   team['id']])
    runner.invoke(['remoteci-create', '--name', 'bar', '--team_id',
                   team['id']])
    result = runner.invoke(['remoteci-list'])
    remotecis = json.loads(result.output)['remotecis']

    assert len(remotecis) == 2
    assert remotecis[0]['name'] == 'foo'
    assert remotecis[1]['name'] == 'bar'


def test_create(runner):
    result = runner.invoke(['team-create', '--name', 'foo'])
    team = json.loads(result.output)['team']
    result = runner.invoke(['remoteci-create', '--name', 'foo', '--team_id',
                            team['id']])
    remoteci = json.loads(result.output)['remoteci']
    assert remoteci['name'] == 'foo'


def test_update(runner):
    result = runner.invoke(['team-create', '--name', 'foo'])
    team = json.loads(result.output)['team']
    result = runner.invoke(['remoteci-create', '--name', 'foo', '--team_id',
                            team['id']])
    remoteci = json.loads(result.output)['remoteci']

    result = runner.invoke(['remoteci-update', '--id', remoteci['id'],
                            '--etag', remoteci['etag'], '--name', 'bar'])
    result = json.loads(result.output)

    assert result['message'] == 'Remote CI updated.'
    assert result['name'] == 'bar'


def test_delete(runner):
    result = runner.invoke(['team-create', '--name', 'foo'])
    team = json.loads(result.output)['team']

    result = runner.invoke(['remoteci-create', '--name', 'foo', '--team_id',
                            team['id']])
    remoteci = json.loads(result.output)['remoteci']

    result = runner.invoke(['remoteci-delete', '--id', remoteci['id'],
                            '--etag', remoteci['etag']])
    result = json.loads(result.output)

    assert result['message'] == 'Remote CI deleted.'


def test_show(runner):
    result = runner.invoke(['team-create', '--name', 'foo'])
    team = json.loads(result.output)['team']
    result = runner.invoke(['remoteci-create', '--name', 'foo', '--team_id',
                            team['id']])
    remoteci = json.loads(result.output)['remoteci']

    result = runner.invoke(['remoteci-show', '--id', remoteci['id']])
    remoteci = json.loads(result.output)['remoteci']

    assert remoteci['name'] == 'foo'
