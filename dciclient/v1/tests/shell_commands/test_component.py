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
import json


def test_prettytable_output(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])
    topic = json.loads(topic.output)['topic']
    assert topic['name'] == 'osp'

    result = runner.invoke(['component-create', '--name', 'foo',
                            '--type', 'bar', '--export_control',
                            '--topic_id', topic['id']])
    component = json.loads(result.output)['component']

    result = runner.invoke(['--format', 'table', 'component-show', '--id',
                            component['id']])

    output = result.output.split('\n')
    # NOTE(spredzy) : The expected output for a table format looks like the
    #                 following :
    #
    # +------------
    # |  id | name
    # +------------
    # | id1 | name1
    # | id2 | name2
    # | id3 | name3
    # +------------
    #
    # The header variable below represents the header data, when more than one
    # space is located between the string and the '|' space number is shrink to
    # one ( this is what ' '.join(string.split()) does
    #
    # The data variable below represents the actual data, when more than one
    # space is located between the string and the '|' space number is shrink to
    # one ( this is what ' '.join(string.split()) does
    header = ' '.join(output[1].split())
    data = ' '.join(output[3].split())

    expected_data = (component['id'],
                     component['name'],
                     component['canonical_project_name'],
                     component['type'],
                     component['title'],
                     component['message'],
                     component['url'],
                     component['created_at'],
                     component['export_control'],
                     component['updated_at'])

    assert header == ('| id | name | canonical_project_name '
                      '| type | title | message | url '
                      '| data | created_at | export_control '
                      '| updated_at |')

    assert data == ('| %s | %s | %s | %s | %s | %s | %s | {} '
                    '| %s | %s | %s |' % expected_data)


def test_list(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])
    topic = json.loads(topic.output)['topic']

    result = runner.invoke(['team-list'])
    teams = json.loads(result.output)['teams']
    team_id = teams[0]['id']

    topic_team = runner.invoke(['topic-attach-team', '--id', topic['id'],
                                '--team_id', team_id])
    topic_team = json.loads(topic_team.output)

    runner.invoke(['component-create', '--name', 'foo', '--type', 'bar',
                   '--topic_id', topic['id']])
    runner.invoke(['component-create', '--name', 'bar', '--type', 'bar2',
                   '--topic_id', topic['id']])
    result = runner.invoke(['component-list', '--topic_id', topic['id']])
    components = json.loads(result.output)['components']

    assert len(components) == 2
    assert components[0]['name'] == 'foo'
    assert components[1]['name'] == 'bar'


def test_create(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])
    topic = json.loads(topic.output)['topic']

    component = runner.invoke(['component-create', '--name', 'foo',
                               '--type', 'foobar', '--topic_id', topic['id']])
    component = json.loads(component.output)['component']
    assert component['name'] == 'foo'


def test_delete(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])
    topic = json.loads(topic.output)['topic']

    result = runner.invoke(['component-create', '--name', 'foo',
                            '--type', 'bar', '--topic_id', topic['id']])
    component = json.loads(result.output)['component']

    result = runner.invoke(['component-delete', '--id', component['id']])
    result = json.loads(result.output)

    assert result['message'] == 'Component deleted.'


def test_show(runner):
    topic = runner.invoke(['topic-create', '--name', 'osp'])
    topic = json.loads(topic.output)['topic']
    assert topic['name'] == 'osp'

    result = runner.invoke(['component-create', '--name', 'foo',
                            '--type', 'bar', '--export_control',
                            '--topic_id', topic['id']])
    component = json.loads(result.output)['component']

    result = runner.invoke(['component-show', '--id', component['id']])
    component = json.loads(result.output)['component']

    assert component['name'] == 'foo'


def test_file_support(runner, tmpdir):
    td = tmpdir
    p = td.join("hello.txt")
    p.write("content")
    topic = runner.invoke(['topic-create', '--name', 'osp'])
    topic = json.loads(topic.output)['topic']

    component = runner.invoke(['component-create', '--name', 'foo',
                               '--type', 'foobar', '--topic_id', topic['id'],
                               '--export_control'])
    component = json.loads(component.output)['component']

    # upload
    result = runner.invoke(['component-file-upload', '--id', component['id'],
                            '--path', p.strpath])
    new_f = json.loads(result.output)['component_file']
    assert new_f['size'] == 7

    # show
    result = runner.invoke(['component-file-show', '--id', component['id'],
                            '--file_id', new_f['id']])
    new_f = json.loads(result.output)['component_file']
    assert new_f['size'] == 7

    # download
    result = runner.invoke(['component-file-download', '--id', component['id'],
                            '--file_id', new_f['id'],
                            '--target', td.strpath + '/my_file'])
    assert open(td.strpath + '/my_file', 'r').read() == 'content'

    # list
    result = runner.invoke(['component-file-list', '--id', component['id']])
    my_list = json.loads(result.output)['component_files']
    assert len(my_list) == 1
    assert my_list[0]['size'] == 7

    # delete
    result = runner.invoke(['component-file-delete', '--id', component['id'],
                            '--file_id', new_f['id']])
    result = runner.invoke(['component-file-show', '--id', component['id'],
                            '--file_id', new_f['id']])
    assert json.loads(result.output)['status_code'] == 404
