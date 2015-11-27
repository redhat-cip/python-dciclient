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
    result = runner.invoke(['componenttype-create', '--name', 'foo'])
    componenttype = json.loads(result.output)['componenttype']

    result = runner.invoke(['--format', 'table', 'componenttype-show', '--id',
                            componenttype['id']])

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

    expected_data = (componenttype['id'], componenttype['name'],
                     componenttype['etag'], componenttype['created_at'],
                     componenttype['updated_at'])

    assert header == '| id | name | etag | created_at | updated_at |'

    assert data == '| %s | %s | %s | %s | %s |' % expected_data


def test_list(runner):
    runner.invoke(['componenttype-create', '--name', 'foo'])
    runner.invoke(['componenttype-create', '--name', 'bar'])
    result = runner.invoke(['componenttype-list'])
    componenttypes = json.loads(result.output)['componenttypes']

    assert len(componenttypes) == 2
    assert componenttypes[0]['name'] == 'foo'
    assert componenttypes[1]['name'] == 'bar'


def test_create(runner):
    result = runner.invoke(['componenttype-create', '--name', 'foo'])
    componenttype = json.loads(result.output)['componenttype']
    assert componenttype['name'] == 'foo'


def test_update(runner):
    result = runner.invoke(['componenttype-create', '--name', 'foo'])
    componenttype = json.loads(result.output)['componenttype']

    result = runner.invoke(['componenttype-update', '--id',
                            componenttype['id'],
                            '--etag', componenttype['etag'], '--name', 'bar'])
    result = json.loads(result.output)

    assert result['message'] == 'Component Type updated.'
    assert result['name'] == 'bar'


def test_delete(runner):
    result = runner.invoke(['componenttype-create', '--name', 'foo'])
    componenttype = json.loads(result.output)['componenttype']

    result = runner.invoke(['componenttype-delete', '--id',
                            componenttype['id'],
                            '--etag', componenttype['etag']])
    result = json.loads(result.output)

    assert result['message'] == 'Component Type deleted.'


def test_show(runner):
    result = runner.invoke(['componenttype-create', '--name', 'foo'])
    componenttype = json.loads(result.output)['componenttype']

    result = runner.invoke(['componenttype-show', '--id',
                            componenttype['id']])
    componenttype = json.loads(result.output)['componenttype']

    assert componenttype['name'] == 'foo'
