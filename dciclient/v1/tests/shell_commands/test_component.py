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


def test_prettytable_output(runner, topic_id):
    component = runner.invoke_raw_parse([
        'component-create',
        '--name', 'osp',
        '--type', 'repo',
        '--topic_id', topic_id])
    assert component['name'] == 'osp'
    assert component == runner.invoke_raw_parse([
        'component-show', component['id']])


def test_list(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']
    teams = runner.invoke(['team-list'])['teams']
    team_id = teams[0]['id']

    runner.invoke(['topic-attach-team', topic['id'],
                   '--team_id', team_id])

    runner.invoke(['component-create', '--name', 'foo', '--type', 'bar',
                   '--topic_id', topic['id']])
    runner.invoke(['component-create', '--name', 'bar', '--type', 'bar2',
                   '--topic_id', topic['id']])
    components = runner.invoke([
        'component-list', '--topic_id', topic['id']])['components']

    assert len(components) == 2
    assert components[0]['name'] == 'bar'
    assert components[1]['name'] == 'foo'


def test_create(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']

    component = runner.invoke(['component-create', '--name', 'foo',
                               '--type', 'foobar', '--topic_id',
                               topic['id']])['component']
    assert component['name'] == 'foo'


def test_delete(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']
    component = runner.invoke(['component-create', '--name', 'foo',
                               '--type', 'bar', '--topic_id',
                               topic['id']])['component']

    result = runner.invoke(['component-delete', component['id']])

    assert result['message'] == 'Component deleted.'


def test_show(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']
    assert topic['name'] == 'osp'

    component = runner.invoke([
        'component-create', '--name', 'foo',
        '--type', 'bar', '--export_control',
        '--topic_id', topic['id']])['component']

    result = runner.invoke(['component-show', component['id']])

    assert result['component']['name'] == 'foo'


def test_file_support(runner, tmpdir):
    td = tmpdir
    p = td.join("hello.txt")
    p.write("content")
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']

    component = runner.invoke(['component-create', '--name', 'foo',
                               '--type', 'foobar', '--topic_id', topic['id'],
                               '--export_control'])['component']

    # upload
    new_f = runner.invoke(['component-file-upload', component['id'],
                           '--path', p.strpath])['component_file']
    assert new_f['size'] == 7

    # show
    new_f = runner.invoke(['component-file-show', component['id'],
                           '--file_id', new_f['id']])['component_file']
    assert new_f['size'] == 7

    # download
    runner.invoke_raw(['component-file-download', component['id'],
                       '--file_id', new_f['id'],
                       '--target', td.strpath + '/my_file'])
    assert open(td.strpath + '/my_file', 'r').read() == 'content'

    # list
    my_list = runner.invoke(['component-file-list',
                             component['id']])['component_files']
    assert len(my_list) == 1
    assert my_list[0]['size'] == 7

    # delete
    runner.invoke_raw([
        'component-file-delete', component['id'],
        '--file_id', new_f['id']])
    result = runner.invoke(['component-file-show', component['id'],
                            '--file_id', new_f['id']])
    assert result['status_code'] == 404


def test_enable_export_control(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']

    component = runner.invoke([
        'component-create', '--name', 'foo',
        '--type', 'bar', '--topic_id',
        topic['id']])['component']

    result = runner.invoke(['component-update', component['id'],
                            '--export-control'])
    assert result['message'] == 'Export Control Enabled.'


def test_disable_export_control(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])['topic']

    component = runner.invoke([
        'component-create', '--name', 'foo',
        '--type', 'bar', '--topic_id',
        topic['id']])['component']

    result = runner.invoke(['component-update', component['id'],
                            '--export-control'])
    assert result['message'] == 'Export Control Enabled.'

    result = runner.invoke(['component-update', component['id'],
                            '--no-export-control'])
    assert result['message'] == 'Export Control Disabled.'


def test_component_status(runner, job_id, topic_id):

    status = runner.invoke(['component-status', '--type', 'type_1',
                            '--topic_id', topic_id])['jobs']

    assert len(status) == 1
    assert status[0]['job_status'] is None
