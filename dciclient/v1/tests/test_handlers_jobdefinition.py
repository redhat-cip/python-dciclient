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
    result = runner.invoke(['test-create', '--name', 'foo'])
    test = json.loads(result.output)['test']

    runner.invoke(['jobdefinition-create', '--name', 'foo', '--test_id',
                   test['id']])
    runner.invoke(['jobdefinition-create', '--name', 'bar', '--test_id',
                   test['id']])
    result = runner.invoke(['jobdefinition-list'])
    jobdefinitions = json.loads(result.output)['jobdefinitions']

    assert len(jobdefinitions) == 2
    assert jobdefinitions[0]['name'] == 'foo'
    assert jobdefinitions[1]['name'] == 'bar'


def test_create(runner):
    result = runner.invoke(['test-create', '--name', 'foo'])
    test = json.loads(result.output)['test']
    result = runner.invoke(['jobdefinition-create', '--name', 'foo',
                            '--test_id', test['id']])
    jobdefinition = json.loads(result.output)['jobdefinition']
    assert jobdefinition['name'] == 'foo'


def test_update(runner):
    result = runner.invoke(['test-create', '--name', 'foo'])
    test = json.loads(result.output)['test']
    result = runner.invoke(['jobdefinition-create', '--name', 'foo',
                            '--test_id', test['id']])
    jobdefinition = json.loads(result.output)['jobdefinition']

    result = runner.invoke(['jobdefinition-update', '--id',
                            jobdefinition['id'], '--etag',
                            jobdefinition['etag'], '--name', 'bar'])
    result = json.loads(result.output)

    assert result['message'] == 'Job Definition updated.'
    assert result['name'] == 'bar'


def test_delete(runner):
    result = runner.invoke(['test-create', '--name', 'foo'])
    test = json.loads(result.output)['test']

    result = runner.invoke(['jobdefinition-create', '--name', 'foo',
                            '--test_id', test['id']])
    jobdefinition = json.loads(result.output)['jobdefinition']

    result = runner.invoke(['jobdefinition-delete', '--id',
                            jobdefinition['id'], '--etag',
                            jobdefinition['etag']])
    result = json.loads(result.output)

    assert result['message'] == 'Job Definition deleted.'


def test_show(runner):
    result = runner.invoke(['test-create', '--name', 'foo'])
    test = json.loads(result.output)['test']
    result = runner.invoke(['jobdefinition-create', '--name', 'foo',
                            '--test_id', test['id']])
    jobdefinition = json.loads(result.output)['jobdefinition']

    result = runner.invoke(['jobdefinition-show', '--id', jobdefinition['id']])
    jobdefinition = json.loads(result.output)['jobdefinition']

    assert jobdefinition['name'] == 'foo'
