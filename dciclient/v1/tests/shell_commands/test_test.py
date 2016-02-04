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
    result = runner.invoke(['test-create', '--name', 'foo'])
    test = json.loads(result.output)['test']

    result = runner.invoke(['--format', 'table', 'test-show', '--id',
                            test['id']])

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

    expected_data = (test['id'], test['name'], test['created_at'])

    assert header == '| id | name | data | created_at |'

    assert data == '| %s | %s | {} | %s |' % expected_data


def test_list(runner):
    runner.invoke(['test-create', '--name', 'foo'])
    runner.invoke(['test-create', '--name', 'bar'])
    result = runner.invoke(['test-list'])
    tests = json.loads(result.output)['tests']
    assert len(tests) == 2
    assert tests[0]['name'] == 'foo'
    assert tests[1]['name'] == 'bar'


def test_create(runner):
    result = runner.invoke(['test-create', '--name', 'foo'])
    test = json.loads(result.output)['test']
    assert test['name'] == 'foo'



def test_delete(runner):
    result = runner.invoke(['test-create', '--name', 'foo'])
    test = json.loads(result.output)['test']

    result = runner.invoke(['test-delete', '--id', test['id']])
    result = json.loads(result.output)

    assert result['message'] == 'Test deleted.'


def test_show(runner):
    result = runner.invoke(['test-create', '--name', 'foo'])
    test = json.loads(result.output)['test']

    result = runner.invoke(['test-show', '--id', test['id']])
    test = json.loads(result.output)['test']

    assert test['name'] == 'foo'
