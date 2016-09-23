# -*- encoding: utf-8 -*-
#
# Copyright 2015-2016 Red Hat, Inc.
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

import io
import requests.adapters
import requests.models
import requests.utils

from dci import auth
from dci.db import models


class FlaskHTTPAdapter(requests.adapters.HTTPAdapter):

    def __init__(self, flask_client):
        super(FlaskHTTPAdapter, self).__init__(pool_connections=1)
        self.client = flask_client

    def init_poolmanager(self, *args, **kwargs):
        pass

    def build_response(self, req, resp):
        response = requests.models.Response()
        response.status_code = resp.status_code

        response.headers = resp.headers
        response.encoding = (
            requests.utils.get_encoding_from_headers(resp.headers) or
            'utf-8'
        )
        response.raw = io.BytesIO(resp.data)
        response.request = req
        response.connection = self
        return response

    def close(self):
        pass

    def send(self, request, stream=False, timeout=None, verify=True,
             cert=None, proxies=None):

        content_type = request.headers.pop('Content-Type', None)
        content_length = request.headers.pop('Content-Length', None)
        # https://github.com/pallets/werkzeug/pull/1011
        if hasattr(request.body, 'read'):
            request.body = request.body.read()

        response = self.client.open(request.path_url,
                                    method=request.method.lower(),
                                    data=request.body,
                                    headers=dict(request.headers),
                                    content_type=content_type,
                                    content_length=content_length)
        return self.build_response(request, response)


def generate_componenttype(client):
    return client.post('/componenttypes', {'name': 'my_component_type'}).json()


def generate_job(client):
    componenttype = generate_componenttype(client)

    test = client.post('/tests', {'name': 'my_test'}).json()
    component = client.post('/components', {
        'name': 'my_component',
        'componenttype_id': componenttype['id'],
        'sha': 'some_sha',
        'canonical_project_name': 'my_project'}
    ).json()

    jobdefinition = client.post('/jobdefinitions', {
        'test_id': test['id'], 'priority': 0
    }).json()

    client.post('/jobdefinition_components', {
        'jobdefinition_id': jobdefinition['id'],
        'component_id': component['id']
    }).json()

    team = client.post('/teams', {
        'name': 'my_team'
    }).json()

    remoteci = client.post('/remotecis', {
        'team_id': team['id']
    }).json()

    job = client.post('/jobs', {
        'team_id': team['id'],
        'jobdefinition_id': jobdefinition['id'],
        'remoteci_id': remoteci['id'],
        'recheck': False
    }).json()

    return job


def provision(db_conn):
    def db_insert(model_item, **kwargs):
        query = model_item.insert().values(**kwargs)
        return db_conn.execute(query).inserted_primary_key[0]

    user_pw_hash = auth.hash_password('user')
    user_admin_pw_hash = auth.hash_password('user_admin')
    admin_pw_hash = auth.hash_password('admin')

    # Create teams
    team_admin_id = db_insert(models.TEAMS, name='admin')
    team_user_id = db_insert(models.TEAMS, name='user')

    # Create users
    db_insert(models.USERS, name='user', role='user', password=user_pw_hash,
              team_id=team_user_id)

    db_insert(models.USERS, name='user_admin', role='admin',
              password=user_admin_pw_hash, team_id=team_user_id)

    db_insert(models.USERS, name='admin', role='admin', password=admin_pw_hash,
              team_id=team_admin_id)
