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
            requests.utils.get_encoding_from_headers(resp.headers) or "utf-8"
        )
        response.raw = io.BytesIO(resp.data)
        response.request = req
        response.connection = self
        return response

    def close(self):
        pass

    def send(
        self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None
    ):

        content_type = request.headers.pop("Content-Type", None)
        content_length = request.headers.pop("Content-Length", None)
        # https://github.com/pallets/werkzeug/pull/1011
        if hasattr(request.body, "read"):
            request.body = request.body.read()

        response = self.client.open(
            request.path_url,
            method=request.method.lower(),
            data=request.body,
            headers=dict(request.headers),
            content_type=content_type,
            content_length=content_length,
        )
        return self.build_response(request, response)


def generate_componenttype(client):
    return client.post("/componenttypes", {"name": "my_component_type"}).json()


def generate_job(client, topic_id):
    componenttype = generate_componenttype(client)

    client.post("/tests", {"name": "my_test"})
    component = client.post(
        "/components",
        {
            "name": "my_component",
            "componenttype_id": componenttype["id"],
            "sha": "some_sha",
            "canonical_project_name": "my_project",
        },
    ).json()

    team = client.post("/teams", {"name": "my_team"}).json()

    remoteci = client.post("/remotecis", {"team_id": team["id"]}).json()

    job = client.post(
        "/jobs",
        {
            "topic_id": topic_id,
            "team_id": team["id"],
            "remoteci_id": remoteci["id"],
            "components": [component["id"]],
        },
    ).json()

    return job


def provision(db_conn):
    def db_insert(model_item, return_pk=True, **kwargs):
        query = model_item.insert().values(**kwargs)
        if return_pk:
            return db_conn.execute(query).inserted_primary_key[0]
        else:
            db_conn.execute(query)

    # Create teams
    team_admin_id = db_insert(models.TEAMS, name="admin")
    db_insert(models.TEAMS, name="Red Hat")
    db_insert(models.TEAMS, name="EPM")
    team_product_id = db_insert(models.TEAMS, name="product")
    team_user_id = db_insert(models.TEAMS, name="user")

    # Create users
    user_pw_hash = auth.hash_password("user")
    u_id = db_insert(
        models.USERS,
        name="user",
        sso_username="user",
        password=user_pw_hash,
        fullname="User",
        email="user@example.org",
        team_id=team_user_id,
    )

    db_insert(
        models.JOIN_USERS_TEAMS, return_pk=False, user_id=u_id, team_id=team_user_id
    )

    user_no_team_pw_hash = auth.hash_password("user_no_team")
    u_id = db_insert(
        models.USERS,
        name="user_no_team",
        sso_username="user_no_team",
        password=user_no_team_pw_hash,
        fullname="User No Team",
        email="user_no_team@example.org",
        team_id=None,
    )

    db_insert(models.JOIN_USERS_TEAMS, return_pk=False, user_id=u_id, team_id=None)

    product_owner_pw_hash = auth.hash_password("product_owner")
    u_id = db_insert(
        models.USERS,
        name="product_owner",
        sso_username="product_owner",
        password=product_owner_pw_hash,
        fullname="Product Owner",
        email="product_ownern@example.org",
        team_id=team_product_id,
    )

    db_insert(
        models.JOIN_USERS_TEAMS, return_pk=False, user_id=u_id, team_id=team_product_id
    )

    admin_pw_hash = auth.hash_password("admin")
    u_id = db_insert(
        models.USERS,
        name="admin",
        sso_username="admin",
        password=admin_pw_hash,
        fullname="Admin",
        email="admin@example.org",
        team_id=team_admin_id,
    )

    db_insert(
        models.JOIN_USERS_TEAMS, return_pk=False, user_id=u_id, team_id=team_admin_id
    )

    # Create a product
    db_insert(
        models.PRODUCTS,
        name="Awesome product",
        label="AWSM",
        description="My Awesome product",
    )
