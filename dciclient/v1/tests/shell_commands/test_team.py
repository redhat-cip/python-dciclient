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
    assert len(teams) == 4


def test_create(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    assert team['name'] == 'foo'


def test_update(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']

    result = runner.invoke(['team-update', team['id'],
                            '--etag', team['etag'], '--name', 'bar'])

    assert result['message'] == 'Team updated.'
    assert result['id'] == team['id']


def test_delete(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']

    result = runner.invoke(['team-delete', team['id'],
                            '--etag', team['etag']])

    assert result['message'] == 'Team deleted.'


def test_show(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']

    team = runner.invoke(['team-show', team['id']])['team']

    assert team['name'] == 'foo'
