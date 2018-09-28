# -*- encoding: utf-8 -*-
#
# Copyright 2016 Red Hat, Inc.
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
    topic = runner.invoke_raw_parse([
        'topic-create', '--name', 'osp'])
    assert topic == runner.invoke_raw_parse([
        'topic-show', topic['id']])


def test_list(runner):
    runner.invoke(['topic-create', '--name', 'osp'])
    runner.invoke(['topic-create', '--name', 'ovirt'])
    topics = runner.invoke(['topic-list'])['topics']

    assert len(topics) == 2
    # assert topics[0]['name'] == 'ovirt'
    # assert topics[1]['name'] == 'osp'


def test_create(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']
    assert topic['name'] == 'osp'
    assert len(topic['component_types']) == 0


def test_create_with_product(runner, product_id):
    topic = runner.invoke(['topic-create', '--name', 'osp',
                           '--product-id', product_id])['topic']
    assert topic['name'] == 'osp'
    assert topic['product_id'] == product_id


def test_create_with_component_types(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp',
                           '--component_types', 'foo,bar'])['topic']
    assert topic['name'] == 'osp'
    assert len(topic['component_types']) == 2
    assert topic['component_types'][0] == 'foo'
    assert topic['component_types'][1] == 'bar'


def test_create_with_data(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp',
                           '--data', '{"foo": "bar"}'])['topic']
    assert topic['name'] == 'osp'
    assert topic['data']['foo'] == 'bar'


def test_create_inactive(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp',
                           '--no-active'])['topic']
    assert topic['state'] == 'inactive'


def test_delete(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']
    result = runner.invoke(['topic-delete', topic['id']])

    assert result['message'] == 'Topic deleted.'


def test_show(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']
    topic = runner.invoke(['topic-show', topic['id']])['topic']

    assert topic['name'] == 'osp'


def test_attach_team(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    assert team['name'] == 'foo'

    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']
    assert topic['name'] == 'osp'

    topic_team = runner.invoke(['topic-attach-team', topic['id'],
                                '--team-id', team['id']])
    assert topic_team['team_id'] == team['id']
    assert topic_team['topic_id'] == topic['id']


def test_list_team(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    assert team['name'] == 'foo'

    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']
    assert topic['name'] == 'osp'

    topic_team = runner.invoke(['topic-attach-team', topic['id'],
                                '--team-id', team['id']])
    assert topic_team['team_id'] == team['id']
    assert topic_team['topic_id'] == topic['id']

    result = runner.invoke(['topic-list-team', topic['id']])['teams']
    assert len(result) == 1
    assert result[0]['name'] == 'foo'


def test_unattach_team(runner):
    team = runner.invoke(['team-create', '--name', 'foo'])['team']
    assert team['name'] == 'foo'

    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']
    assert topic['name'] == 'osp'

    topic_team = runner.invoke(['topic-attach-team', topic['id'],
                                '--team-id', team['id']])
    assert topic_team['team_id'] == team['id']
    assert topic_team['topic_id'] == topic['id']

    result = runner.invoke(['topic-list-team', topic['id']])['teams']
    assert len(result) == 1
    assert result[0]['name'] == 'foo'

    topic_team = runner.invoke(['topic-unattach-team', topic['id'],
                                '--team-id', team['id']])

    teams = runner.invoke(['topic-list-team', topic['id']])['teams']
    assert len(teams) == 0


def test_update_active(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']
    assert topic['state'] == 'active'

    result = runner.invoke(['topic-update', topic['id'],
                            '--etag', topic['etag'], '--no-active'])

    assert result['topic']['id'] == topic['id']
    assert result['topic']['state'] == 'inactive'

    result = runner.invoke(['topic-update', topic['id'],
                            '--etag', result['topic']['etag'],
                            '--name', 'foobar'])

    assert result['topic']['id'] == topic['id']
    assert result['topic']['state'] == 'inactive'
    assert result['topic']['name'] == 'foobar'

    result = runner.invoke(['topic-update', topic['id'],
                            '--etag', result['topic']['etag'],
                            '--active'])

    assert result['topic']['state'] == 'active'


def test_update_with_component_types(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']
    result = runner.invoke(['topic-update', topic['id'],
                            '--etag', topic['etag'],
                            '--component_types', 'foo,bar'])

    assert result['topic']['id'] == topic['id']
    assert len(result['topic']['component_types']) == 2
    assert result['topic']['component_types'][0] == 'foo'
    assert result['topic']['component_types'][1] == 'bar'


def test_update_with_data(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']
    result = runner.invoke(['topic-update', topic['id'],
                            '--etag', topic['etag'],
                            '--data', '{"foo": "bar"}'])

    assert result['topic']['id'] == topic['id']
    assert result['topic']['data']['foo'] == 'bar'


def test_where_on_list(runner):
    runner.invoke(['topic-create', '--name', 'osp1'])
    runner.invoke(['topic-create', '--name', 'osp2'])
    assert runner.invoke(['topic-list', '--where',
                          'name:osp1'])["_meta"]["count"]
