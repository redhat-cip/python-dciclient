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
    remoteci = json.loads(result.output)['componenttype']

    result = runner.invoke(['componenttype-update', '--id', remoteci['id'],
                            '--etag', remoteci['etag'], '--name', 'bar'])
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
