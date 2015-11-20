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

import dciclient.v1.shell_commands.remoteci as remoteci


def test_list(http_session, print_json_calls):
    remoteci.create(http_session, 'foo')
    remoteci.create(http_session, 'bar')
    remoteci.list(http_session)

    assert len(print_json_calls[-1]['remotecis']) == 2


def test_create(http_session, print_json_calls):
    remoteci.create(http_session, 'foo')

    assert print_json_calls[-1]['remoteci']['name'] == 'foo'


def test_update(http_session, print_json_calls):
    remoteci.create(http_session, 'foo')
    etag = print_json_calls[-1]['remoteci']['etag']
    id = print_json_calls[-1]['remoteci']['id']
    remoteci.update(http_session, id, etag, 'bar')

    assert print_json_calls[-1]['message'] == 'Remote CI updated.'
    assert print_json_calls[-1]['name'] == 'bar'


def test_delete(http_session, print_json_calls):
    remoteci.create(http_session, 'foo')
    etag = print_json_calls[-1]['remoteci']['etag']
    id = print_json_calls[-1]['remoteci']['id']
    remoteci.delete(http_session, id, etag)

    assert print_json_calls[-1]['message'] == 'Remote CI deleted.'


def test_show(http_session, print_json_calls):
    remoteci.create(http_session, 'foo')
    id = print_json_calls[-1]['remoteci']['id']
    remoteci.show(http_session, id)

    assert print_json_calls[-1]['remoteci']['name'] == 'foo'
