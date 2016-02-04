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


def test_prettytable_output(runner):
    result = runner.invoke(['component-create', '--name', 'foo',
                            '--type', 'bar'])
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

    expected_data = (component['id'], component['name'],
                     component['canonical_project_name'],
                     component['type'], component['sha'],
                     component['title'], component['message'],
                     component['url'], component['git'], component['ref'],
                     component['created_at'])

    assert header == ('| id | name | canonical_project_name '
                      '| type | sha | title | message | url | git '
                      '| ref | data | created_at |')

    assert data == ('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | {} '
                    '| %s |' % expected_data)


def test_list(runner):
    runner.invoke(['component-create', '--name', 'foo', '--type', 'bar'])
    runner.invoke(['component-create', '--name', 'bar', '--type', 'bar2'])
    result = runner.invoke(['component-list'])
    components = json.loads(result.output)['components']

    assert len(components) == 2
    assert components[0]['name'] == 'foo'
    assert components[1]['name'] == 'bar'


def test_create(runner):
    component = runner.invoke(['component-create', '--name', 'foo',
                               '--type', 'foobar'])
    component = json.loads(component.output)['component']
    assert component['name'] == 'foo'


def test_delete(runner):
    result = runner.invoke(['component-create', '--name', 'foo',
                            '--type', 'bar'])
    component = json.loads(result.output)['component']

    result = runner.invoke(['component-delete', '--id',
                            component['id']])
    result = json.loads(result.output)

    assert result['message'] == 'Component deleted.'


def test_show(runner):
    result = runner.invoke(['component-create', '--name', 'foo',
                            '--type', 'bar'])
    component = json.loads(result.output)['component']

    result = runner.invoke(['component-show', '--id', component['id']])
    component = json.loads(result.output)['component']

    assert component['name'] == 'foo'
