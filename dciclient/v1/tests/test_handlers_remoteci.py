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
import dciclient.v1.shell_commands.team as team


def test_list(http_session, print_json_calls):
    team.create(http_session, name='team42')
    team_id = print_json_calls[-1]['team']['id']
    remoteci.create(http_session, name='foo', team_id=team_id, data='{}')
    remoteci.create(http_session, name='bar', team_id=team_id, data='{}')
    remoteci.list(http_session)

    assert len(print_json_calls[-1]['remotecis']) == 2


def test_create(http_session, print_json_calls):
    team.create(http_session, name='team42')
    team_id = print_json_calls[-1]['team']['id']
    remoteci.create(http_session, name='foo', team_id=team_id, data='{}')

    assert print_json_calls[-1]['remoteci']['name'] == 'foo'


def test_update(http_session, print_json_calls):
    team.create(http_session, name='team42')
    team_id = print_json_calls[-1]['team']['id']
    remoteci.create(http_session, name='foo', team_id=team_id, data='{}')
    etag = print_json_calls[-1]['remoteci']['etag']
    id = print_json_calls[-1]['remoteci']['id']
    remoteci.update(http_session, id=id, etag=etag, name='bar',
                    team_id=team_id, data='{}')

    assert print_json_calls[-1]['message'] == 'Remote CI updated.'
    assert print_json_calls[-1]['name'] == 'bar'


def test_delete(http_session, print_json_calls):
    team.create(http_session, name='team42')
    team_id = print_json_calls[-1]['team']['id']
    remoteci.create(http_session, name='foo', team_id=team_id, data='{}')
    etag = print_json_calls[-1]['remoteci']['etag']
    id = print_json_calls[-1]['remoteci']['id']
    remoteci.delete(http_session, id=id, etag=etag)

    assert print_json_calls[-1]['message'] == 'Remote CI deleted.'


def test_show(http_session, print_json_calls):
    team.create(http_session, name='team42')
    team_id = print_json_calls[-1]['team']['id']
    remoteci.create(http_session, name='foo', team_id=team_id, data='{}')
    id = print_json_calls[-1]['remoteci']['id']
    remoteci.show(http_session, id=id)

    assert print_json_calls[-1]['remoteci']['name'] == 'foo'
