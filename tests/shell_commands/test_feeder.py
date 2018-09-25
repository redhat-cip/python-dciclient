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
    feeder = runner.invoke_raw_parse([
        'feeder-create',
        '--name', 'foo'])
    assert feeder['name'] == 'foo'
    assert feeder == runner.invoke_raw_parse([
        'feeder-show', feeder['id']])


def test_list(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    runner.invoke(['feeder-create', '--name', 'foo', '--team-id',
                   team['id']])
    runner.invoke(['feeder-create', '--name', 'bar', '--team-id',
                   team['id']])
    feeders = runner.invoke(['feeder-list'])['feeders']

    assert len(feeders) == 2
    assert feeders[0]['name'] == 'bar'
    assert feeders[1]['name'] == 'foo'


def test_create(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    feeder = runner.invoke([
        'feeder-create', '--name', 'foo', '--team-id',
        team['id']])['feeder']
    assert feeder['name'] == 'foo'
    assert feeder['state'] == 'active'


def test_create_inactive(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    feeder = runner.invoke([
        'feeder-create', '--name', 'foo', '--team-id',
        team['id'], '--no-active'])['feeder']
    assert feeder['state'] == 'inactive'


def test_update(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    feeder = runner.invoke([
        'feeder-create', '--name', 'foo', '--team-id',
        team['id']])['feeder']

    assert feeder['state'] == 'active'

    result = runner.invoke(['feeder-update', feeder['id'],
                            '--etag', feeder['etag'], '--name', 'bar',
                            '--no-active'])

    assert result['feeder']['id'] == feeder['id']
    assert result['feeder']['state'] == 'inactive'


def test_delete(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']

    feeder = runner.invoke([
        'feeder-create', '--name', 'foo', '--team-id',
        team['id']])['feeder']

    result = runner.invoke(['feeder-delete', feeder['id'],
                            '--etag', feeder['etag']])

    assert result['message'] == 'Feeder deleted.'


def test_show(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    feeder = runner.invoke([
        'feeder-create', '--name', 'foo', '--team-id',
        team['id']])['feeder']

    feeder = runner.invoke(['feeder-show', feeder['id']])['feeder']

    assert feeder['name'] == 'foo'
