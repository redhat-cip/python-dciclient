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

import dciclient.v1.shell_commands.test as test


def test_list(http_session, print_json_calls):
    test.create(http_session, name='foo')
    test.create(http_session, name='bar')
    test.list(http_session)

    assert len(print_json_calls[-1]['tests']) == 2


def test_create(http_session, print_json_calls):
    test.create(http_session, name='foo')

    assert print_json_calls[-1]['test']['name'] == 'foo'


def test_update(http_session, print_json_calls):
    test.create(http_session, name='foo')
    etag = print_json_calls[-1]['test']['etag']
    id = print_json_calls[-1]['test']['id']
    test.update(http_session, id=id, etag=etag, name='bar')

    assert print_json_calls[-1]['message'] == 'Test updated.'
    assert print_json_calls[-1]['name'] == 'bar'


def test_delete(http_session, print_json_calls):
    test.create(http_session, name='foo')
    etag = print_json_calls[-1]['test']['etag']
    id = print_json_calls[-1]['test']['id']
    test.delete(http_session, id=id, etag=etag)

    assert print_json_calls[-1]['message'] == 'Test deleted.'


def test_show(http_session, print_json_calls):
    test.create(http_session, name='foo')
    id = print_json_calls[-1]['test']['id']
    test.show(http_session, id=id)

    assert print_json_calls[-1]['test']['name'] == 'foo'
