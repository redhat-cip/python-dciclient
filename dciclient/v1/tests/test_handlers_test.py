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
    header = ' '.join(output[1].split())
    data = ' '.join(output[3].split())

    assert header == "| id | name | data | etag | created_at | updated_at |"
    assert data == "| %s | %s | {} | %s | %s | %s |" % (
        test['id'], test['name'], test['etag'], test['created_at'],
        test['updated_at'])


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


def test_update(runner):
    result = runner.invoke(['test-create', '--name', 'foo'])
    test = json.loads(result.output)['test']

    result = runner.invoke(['test-update', '--id', test['id'],
                            '--etag', test['etag'], '--name', 'bar'])
    result = json.loads(result.output)

    assert result['message'] == 'Test updated.'
    assert result['name'] == 'bar'


def test_delete(runner):
    result = runner.invoke(['test-create', '--name', 'foo'])
    test = json.loads(result.output)['test']

    result = runner.invoke(['test-delete', '--id', test['id'],
                            '--etag', test['etag']])
    result = json.loads(result.output)

    assert result['message'] == 'Test deleted.'


def test_show(runner):
    result = runner.invoke(['test-create', '--name', 'foo'])
    test = json.loads(result.output)['test']

    result = runner.invoke(['test-show', '--id', test['id']])
    test = json.loads(result.output)['test']

    assert test['name'] == 'foo'
