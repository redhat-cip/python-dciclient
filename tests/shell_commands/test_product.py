# -*- encoding: utf-8 -*-
#
# Copyright 2017 Red Hat, Inc.
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


def test_prettytable_output(runner, team_id):
    product = runner.invoke_raw_parse([
        'product-create',
        '--name', 'foo', '--team-id', team_id])
    assert product['name'] == 'foo'
    assert product == runner.invoke_raw_parse([
        'product-show', product['id']])
    assert 'etag' not in runner.invoke_raw_parse(['product-list'])
    assert 'etag' in runner.invoke_raw_parse(['product-list', '--long'])


def test_success_create_basic(runner, team_id):
    product = runner.invoke(['product-create', '--name',
                             'myproduct', '--team-id', team_id])['product']
    assert product['name'] == 'myproduct'


def test_success_create_full(runner, team_id):
    product = runner.invoke(['product-create', '--name', 'myproduct',
                             '--label', 'MYPRODUCT', '--description',
                             'myproduct', '--active', '--team-id',
                             team_id])['product']
    assert product['name'] == 'myproduct'
    assert product['label'] == 'MYPRODUCT'
    assert product['description'] == 'myproduct'
    assert product['state'] == 'active'


def test_create_inactive(runner, team_id):
    product = runner.invoke(['product-create', '--name', 'myproduct',
                             '--no-active', '--team-id', team_id])['product']
    assert product['state'] == 'inactive'


def test_list(runner, team_id):
    products_number = len(runner.invoke(['product-list'])['products'])

    runner.invoke(['product-create', '--name', 'foo', '--team-id', team_id])
    runner.invoke(['product-create', '--name', 'bar', '--team-id', team_id])

    products_new_number = len(runner.invoke(['product-list'])['products'])

    assert products_new_number == products_number + 2


def test_fail_create_unauthorized_user_admin(runner_user_admin, team_id):
    product = runner_user_admin.invoke(['product-create', '--name', 'foo',
                                        '--team-id', team_id])
    assert product['status_code'] == 401


def test_fail_create_unauthorized_user(runner_user, team_id):
    product = runner_user.invoke(['product-create', '--name', 'foo',
                                  '--team-id', team_id])
    assert product['status_code'] == 401


def test_success_update(runner, team_id):
    product = runner.invoke(['product-create', '--name', 'foo',
                             '--description', 'foo_desc', '--team-id',
                             team_id])['product']

    result = runner.invoke(['product-update', product['id'],
                            '--etag', product['etag'], '--name', 'bar',
                            '--description', 'bar_desc'])

    assert result['product']['id'] == product['id']
    assert result['product']['name'] == 'bar'
    assert result['product']['description'] == 'bar_desc'


def test_update_active(runner, team_id):
    product = runner.invoke(['product-create', '--name',
                             'myproduct', '--team-id', team_id])['product']
    assert product['state'] == 'active'

    result = runner.invoke(['product-update', product['id'],
                            '--etag', product['etag'], '--no-active'])

    assert result['product']['id'] == product['id']
    assert result['product']['state'] == 'inactive'

    result = runner.invoke(['product-update', product['id'],
                            '--etag', result['product']['etag'],
                            '--name', 'foobar'])

    assert result['product']['state'] == 'inactive'

    result = runner.invoke(['product-update', product['id'],
                            '--etag', result['product']['etag'],
                            '--active'])

    assert result['product']['state'] == 'active'


def test_delete(runner, team_id):
    product = runner.invoke(['product-create', '--name', 'foo', '--team-id',
                             team_id])['product']

    result = runner.invoke(['product-delete', product['id'],
                            '--etag', product['etag']])

    assert result['message'] == 'Product deleted.'

    result = runner.invoke(['product-show', product['id']])

    assert result['status_code'] == 404


def test_show(runner, team_id):
    product = runner.invoke(['product-create', '--name', 'foo',
                             '--team-id', team_id])['product']

    product = runner.invoke(['product-show', product['id']])['product']

    assert product['name'] == 'foo'
