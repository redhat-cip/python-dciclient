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
import json


def test_list(http_session, capsys):
    test.create(http_session, 'foo')
    test.create(http_session, 'bar')
    test.list(http_session)
    out, _ = capsys.readouterr()
    out = json.loads(out)

    assert len(out['tests']) == 2

def test_create(http_session, capsys):
    test.create(http_session, 'foo')
    out, _ = capsys.readouterr()
    out = json.loads(out)

    assert out['test']['name'] == 'foo'

def test_update(http_session, capsys):
    test.create(http_session, 'foo')
    out, _ = capsys.readouterr()
    out = json.loads(out)
    etag = out['test']['etag']
    id = out['test']['id']
    test.update(http_session, id, etag, 'bar')
    out, _ = capsys.readouterr()
    out = json.loads(out)

    assert out['message'] == 'Test updated.'
    assert out['name'] == 'bar'

def test_delete(http_session, capsys):
    test.create(http_session, 'foo')
    out, _ = capsys.readouterr()
    out = json.loads(out)
    etag = out['test']['etag']
    id = out['test']['id']
    test.delete(http_session, id, etag)
    out, _ = capsys.readouterr()
    out = json.loads(out)

    assert out['message'] == 'Test deleted.'

def test_show(http_session, capsys):
    test.create(http_session, 'foo')
    out, _ = capsys.readouterr()
    out = json.loads(out)
    id = out['test']['id']
    test.show(http_session, id)
    out, _ = capsys.readouterr()
    out = json.loads(out)

    assert out['test']['name'] == 'foo'
