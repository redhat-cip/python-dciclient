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


def generate_job(client, topic_id):
    componenttype = generate_componenttype(client)

    client.post('/tests', {'name': 'my_test'})
    component = client.post('/components', {
        'name': 'my_component',
        'componenttype_id': componenttype['id'],
        'sha': 'some_sha',
        'canonical_project_name': 'my_project'}
    ).json()

    team = client.post('/teams', {
        'name': 'my_team'
    }).json()

    remoteci = client.post('/remotecis', {
        'team_id': team['id']
    }).json()

    job = client.post('/jobs', {
        'topic_id': topic_id,
        'team_id': team['id'],
        'remoteci_id': remoteci['id'],
        'components': [component['id']]
    }).json()

    return job


def provision(db_conn):
    def db_insert(model_item, **kwargs):
        query = model_item.insert().values(**kwargs)
        return db_conn.execute(query).inserted_primary_key[0]

    user_pw_hash = auth.hash_password('user')
    user_admin_pw_hash = auth.hash_password('user_admin')
    product_owner_pw_hash = auth.hash_password('product_owner')
    admin_pw_hash = auth.hash_password('admin')

    # Create teams
    team_admin_id = db_insert(models.TEAMS, name='admin')
    team_product_id = db_insert(models.TEAMS, name='product')
    team_user_id = db_insert(models.TEAMS, name='user',
                             parent_id=team_product_id)

    # Create the four mandatory roles
    super_admin_role = {
        'name': 'Super Admin',
        'label': 'SUPER_ADMIN',
        'description': 'Admin of the platform',
    }

    product_owner_role = {
        'name': 'Product Owner',
        'label': 'PRODUCT_OWNER',
        'description': 'Product Owner',
    }

    admin_role = {
        'name': 'Admin',
        'label': 'ADMIN',
        'description': 'Admin of a team',
    }

    user_role = {
        'name': 'User',
        'label': 'USER',
        'description': 'Regular User',
    }

    remoteci_role = {
        'name': 'RemoteCI',
        'label': 'REMOTECI',
        'description': 'A RemoteCI',
    }

    feeder_role = {
        'name': 'Feeder',
        'label': 'FEEDER',
        'description': 'A Feeder',
    }

    super_admin_role_id = db_insert(models.ROLES, **super_admin_role)
    admin_role_id = db_insert(models.ROLES, **admin_role)
    user_role_id = db_insert(models.ROLES, **user_role)
    product_owner_role_id = db_insert(models.ROLES, **product_owner_role)
    db_insert(models.ROLES, **remoteci_role)
    db_insert(models.ROLES, **feeder_role)

    # Create users
    db_insert(models.USERS, name='user', role_id=user_role_id,
              password=user_pw_hash, team_id=team_user_id,
              fullname='User', email='user@example.org')

    db_insert(models.USERS, name='user_admin', role_id=admin_role_id,
              password=user_admin_pw_hash, team_id=team_user_id,
              fullname='User Admin', email='user_admin@example.org')

    db_insert(models.USERS, name='admin', role_id=super_admin_role_id,
              password=admin_pw_hash, team_id=team_admin_id,
              fullname='Admin', email='admin@example.org')

    db_insert(models.USERS,
              name='product_owner',
              sso_username='product_owner',
              role_id=product_owner_role_id,
              password=product_owner_pw_hash,
              fullname='Product Owner',
              email='product_ownern@example.org',
              team_id=team_product_id)
