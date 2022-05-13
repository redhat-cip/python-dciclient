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
from dci.db import models2


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


def provision(session):
    # Create admin
    admin_team = models2.Team(name="admin")
    admin_user = models2.User(
        name="admin",
        sso_username="admin",
        password=auth.hash_password("admin"),
        fullname="Admin",
        email="admin@example.org",
    )
    admin_user.team.append(admin_team)
    session.add(admin_user)

    # Create user
    user_team = models2.Team(name="user")
    user = models2.User(
        name="user",
        sso_username="user",
        password=auth.hash_password("user"),
        fullname="User",
        email="user@example.org",
    )
    user.team.append(user_team)
    session.add(user)

    # Create user no team
    user_no_team = models2.User(
        name="user_no_team",
        sso_username="user_no_team",
        password=auth.hash_password("user_no_team"),
        fullname="User No Team",
        email="user_no_team@example.org",
    )
    session.add(user_no_team)

    # Create product_owner
    user_no_team = models2.User(
        name="product_owner",
        sso_username="product_owner",
        password=auth.hash_password("product_owner"),
        fullname="Product Owner",
        email="product_owner@example.org",
    )
    session.add(user_no_team)

    # Create EPM team
    session.add(models2.Team(name="EPM"))

    # Create Red Hat team
    red_hat = models2.Team(name="Red Hat")
    session.add(red_hat)

    # Create Red Hat employee
    rh_employee = models2.User(
        name="rh_employee",
        sso_username="rh_employee",
        password=auth.hash_password("rh_employee"),
        fullname="Employee at Red Hat",
        email="rh_employee@redhat.com",
    )
    rh_employee.team.append(red_hat)
    session.add(rh_employee)

    # Create a product
    product = models2.Product(
        name="dci_product",
        label="dci_product",
        description="My Awesome product",
    )
    user_team.products.append(product)
    session.add(user_team)

    session.commit()
