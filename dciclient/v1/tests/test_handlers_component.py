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
    result = runner.invoke(['componenttype-create', '--name', 'foo'])
    componenttype = json.loads(result.output)['componenttype']

    runner.invoke(['component-create', '--name', 'foo', '--componenttype_id',
                   componenttype['id']])
    runner.invoke(['component-create', '--name', 'bar', '--componenttype_id',
                   componenttype['id']])
    result = runner.invoke(['component-list'])
    components = json.loads(result.output)['components']

    assert len(components) == 2
    assert components[0]['name'] == 'foo'
    assert components[1]['name'] == 'bar'


def test_create(runner):
    result = runner.invoke(['componenttype-create', '--name', 'foo'])
    componenttype = json.loads(result.output)['componenttype']
    result = runner.invoke(['component-create', '--name', 'foo',
                            '--componenttype_id', componenttype['id']])
    component = json.loads(result.output)['component']
    assert component['name'] == 'foo'


def test_delete(runner):
    result = runner.invoke(['componenttype-create', '--name', 'foo'])
    componenttype = json.loads(result.output)['componenttype']

    result = runner.invoke(['component-create', '--name', 'foo',
                            '--componenttype_id', componenttype['id']])
    component = json.loads(result.output)['component']

    result = runner.invoke(['component-delete', '--id',
                            component['id'], '--etag',
                            component['etag']])
    result = json.loads(result.output)

    assert result['message'] == 'Component deleted.'


def test_show(runner):
    result = runner.invoke(['componenttype-create', '--name', 'foo'])
    componenttype = json.loads(result.output)['componenttype']
    result = runner.invoke(['component-create', '--name', 'foo',
                            '--componenttype_id', componenttype['id']])
    component = json.loads(result.output)['component']

    result = runner.invoke(['component-show', '--id', component['id']])
    component = json.loads(result.output)['component']

    assert component['name'] == 'foo'
