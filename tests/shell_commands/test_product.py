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


def test_success_create_basic(runner):
    product = runner.invoke(["product-create", "--name", "myproduct"])["product"]
    assert product["name"] == "myproduct"


def test_success_create_full(runner):
    product = runner.invoke(
        [
            "product-create",
            "--name",
            "myproduct",
            "--label",
            "MYPRODUCT",
            "--description",
            "myproduct",
            "--active",
        ]
    )["product"]
    assert product["name"] == "myproduct"
    assert product["label"] == "MYPRODUCT"
    assert product["description"] == "myproduct"
    assert product["state"] == "active"


def test_create_inactive(runner):
    product = runner.invoke(["product-create", "--name", "myproduct", "--no-active"])[
        "product"
    ]
    assert product["state"] == "inactive"


def test_list(runner):
    products_number = len(runner.invoke(["product-list"])["products"])

    runner.invoke(["product-create", "--name", "foo"])
    runner.invoke(["product-create", "--name", "bar"])

    products_new_number = len(runner.invoke(["product-list"])["products"])

    assert products_new_number == products_number + 2


def test_fail_create_unauthorized_user_admin(runner_user_admin):
    product = runner_user_admin.invoke_raw(["product-create", "--name", "foo"])
    assert product.status_code == 401


def test_fail_create_unauthorized_user(runner_user):
    product = runner_user.invoke_raw(["product-create", "--name", "foo"])
    assert product.status_code == 401


def test_success_update(runner):
    product = runner.invoke(
        ["product-create", "--name", "foo", "--description", "foo_desc"]
    )["product"]

    result = runner.invoke(
        [
            "product-update",
            product["id"],
            "--etag",
            product["etag"],
            "--name",
            "bar",
            "--description",
            "bar_desc",
        ]
    )

    assert result["product"]["id"] == product["id"]
    assert result["product"]["name"] == "bar"
    assert result["product"]["description"] == "bar_desc"


def test_update_active(runner):
    product = runner.invoke(["product-create", "--name", "myproduct"])["product"]
    assert product["state"] == "active"

    result = runner.invoke(
        ["product-update", product["id"], "--etag", product["etag"], "--no-active"]
    )

    assert result["product"]["id"] == product["id"]
    assert result["product"]["state"] == "inactive"

    result = runner.invoke(
        [
            "product-update",
            product["id"],
            "--etag",
            result["product"]["etag"],
            "--name",
            "foobar",
        ]
    )

    assert result["product"]["state"] == "inactive"

    result = runner.invoke(
        [
            "product-update",
            product["id"],
            "--etag",
            result["product"]["etag"],
            "--active",
        ]
    )

    assert result["product"]["state"] == "active"


def test_delete(runner):
    product = runner.invoke(["product-create", "--name", "foo"])["product"]

    result = runner.invoke_raw(
        ["product-delete", product["id"], "--etag", product["etag"]]
    )

    assert result.status_code == 204

    result = runner.invoke_raw(["product-show", product["id"]])

    assert result.status_code == 404


def test_show(runner):
    product = runner.invoke(["product-create", "--name", "foo"])["product"]

    product = runner.invoke(["product-show", product["id"]])["product"]

    assert product["name"] == "foo"


def test_list_teams_empty(runner, product_id, team_id):
    no_teams = runner.invoke(["product-list-teams", product_id])
    assert no_teams["_meta"]["count"] == 0
    assert len(no_teams["teams"]) == 0


def test_attach_team_and_list(runner, product_id, team_id):
    no_teams = runner.invoke(["product-list-teams", product_id])
    assert no_teams["_meta"]["count"] == 0
    assert len(no_teams["teams"]) == 0

    attached = runner.invoke(["product-attach-team", product_id, "--team-id", team_id])

    assert attached["product_id"] == product_id
    assert attached["team_id"] == team_id

    one_team = runner.invoke(["product-list-teams", product_id])
    assert one_team["_meta"]["count"] == 1
    assert len(one_team["teams"]) == 1
    assert one_team["teams"][0]["id"] == team_id


def test_attach_detach_team_and_list(runner, product_id, team_id):
    no_teams = runner.invoke(["product-list-teams", product_id])
    assert no_teams["_meta"]["count"] == 0
    assert len(no_teams["teams"]) == 0

    attached = runner.invoke(["product-attach-team", product_id, "--team-id", team_id])

    assert attached["product_id"] == product_id
    assert attached["team_id"] == team_id

    one_team = runner.invoke(["product-list-teams", product_id])

    assert one_team["_meta"]["count"] == 1
    assert len(one_team["teams"]) == 1
    assert one_team["teams"][0]["id"] == team_id

    runner.invoke_raw(["product-detach-team", product_id, "--team-id", team_id])
    no_teams_again = runner.invoke(["product-list-teams", product_id])
    assert no_teams_again["_meta"]["count"] == 0
    assert len(no_teams_again["teams"]) == 0
