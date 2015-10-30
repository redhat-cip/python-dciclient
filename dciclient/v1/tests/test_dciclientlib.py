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


def test_create_get_componenttype(client_v1):
    result = client_v1.create_componenttype('lol1')
    assert result.status_code == 201

    result = client_v1.get_componenttype('lol1')
    assert result.status_code == 200
    ct_id = result.json()['componenttype']['id']

    result = client_v1.get_componenttype(ct_id)
    assert result.status_code == 200


def test_put_componenttype(client_v1):
    result = client_v1.create_componenttype('lol1')
    ct_id = result.json()['componenttype']['id']
    etag = result.headers.get('ETag')

    result = client_v1.put_componenttype(ct_id, etag, 'lol2')
    assert result.status_code == 204

    result = client_v1.get_componenttype('lol1')
    assert result.status_code == 404

    result = client_v1.get_componenttype('lol2')
    assert result.status_code == 200


def test_delete_componenttype(client_v1):
    result = client_v1.create_componenttype('lol1')
    etag = result.headers.get('ETag')
    assert result.status_code == 201

    result = client_v1.get_componenttype('lol1')
    assert result.status_code == 200

    result = client_v1.delete_componenttype('lol1', etag)
    assert result.status_code == 204

    result = client_v1.get_componenttype('lol1')
    assert result.status_code == 404
