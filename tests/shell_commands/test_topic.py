# -*- encoding: utf-8 -*-
#
# Copyright 2016 Red Hat, Inc.
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


def test_list(runner, product_id):
    runner.invoke(["topic-create", "--name", "osp", "--product-id", product_id])
    runner.invoke(["topic-create", "--name", "ovirt", "--product-id", product_id])
    topics = runner.invoke(["topic-list"])["topics"]

    assert len(topics) == 2
    # assert topics[0]['name'] == 'ovirt'
    # assert topics[1]['name'] == 'osp'


def test_create(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    assert topic["name"] == "osp"
    assert len(topic["component_types"]) == 0


def test_create_with_component_types(runner, product_id):
    topic = runner.invoke(
        [
            "topic-create",
            "--name",
            "osp",
            "--product-id",
            product_id,
            "--component_types",
            "foo,bar",
        ]
    )["topic"]
    assert topic["name"] == "osp"
    assert len(topic["component_types"]) == 2
    assert topic["component_types"][0] == "foo"
    assert topic["component_types"][1] == "bar"


def test_create_with_data(runner, product_id):
    topic = runner.invoke(
        [
            "topic-create",
            "--name",
            "osp",
            "--product-id",
            product_id,
            "--data",
            '{"foo": "bar"}',
        ]
    )["topic"]
    assert topic["name"] == "osp"
    assert topic["data"]["foo"] == "bar"


def test_create_inactive(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id, "--no-active"]
    )["topic"]
    assert topic["state"] == "inactive"


def test_create_export_control_default(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    assert topic["export_control"] is False


def test_create_export_control(runner, product_id):
    topic = runner.invoke(
        [
            "topic-create",
            "--name",
            "osp",
            "--product-id",
            product_id,
            "--export-control",
        ]
    )["topic"]
    assert topic["export_control"] is True


def test_create_no_export_control(runner, product_id):
    topic = runner.invoke(
        [
            "topic-create",
            "--name",
            "osp",
            "--product-id",
            product_id,
            "--no-export-control",
        ]
    )["topic"]
    assert topic["export_control"] is False


def test_delete(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    result = runner.invoke_raw(["topic-delete", topic["id"]])

    assert result.status_code == 204


def test_show(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    topic = runner.invoke(["topic-show", topic["id"]])["topic"]

    assert topic["name"] == "osp"


def test_attach_team(runner, product_id):
    team = runner.invoke(["team-create", "--name", "foo"])["team"]
    assert team["name"] == "foo"

    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    assert topic["name"] == "osp"

    topic_team = runner.invoke(
        ["topic-attach-team", topic["id"], "--team-id", team["id"]]
    )
    assert topic_team["team_id"] == team["id"]
    assert topic_team["topic_id"] == topic["id"]


def test_list_team(runner, product_id):
    team = runner.invoke(["team-create", "--name", "foo"])["team"]
    assert team["name"] == "foo"

    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    assert topic["name"] == "osp"

    topic_team = runner.invoke(
        ["topic-attach-team", topic["id"], "--team-id", team["id"]]
    )
    assert topic_team["team_id"] == team["id"]
    assert topic_team["topic_id"] == topic["id"]

    result = runner.invoke(["topic-list-team", topic["id"]])["teams"]
    assert len(result) == 1
    assert result[0]["name"] == "foo"


def test_unattach_team(runner, product_id):
    team = runner.invoke(["team-create", "--name", "foo"])["team"]
    assert team["name"] == "foo"

    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    assert topic["name"] == "osp"

    topic_team = runner.invoke(
        ["topic-attach-team", topic["id"], "--team-id", team["id"]]
    )
    assert topic_team["team_id"] == team["id"]
    assert topic_team["topic_id"] == topic["id"]

    result = runner.invoke(["topic-list-team", topic["id"]])["teams"]
    assert len(result) == 1
    assert result[0]["name"] == "foo"

    topic_team = runner.invoke_raw(
        ["topic-unattach-team", topic["id"], "--team-id", team["id"]]
    )

    teams = runner.invoke(["topic-list-team", topic["id"]])["teams"]
    assert len(teams) == 0


def test_update_active(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    assert topic["state"] == "active"

    result = runner.invoke(
        ["topic-update", topic["id"], "--etag", topic["etag"], "--no-active"]
    )

    assert result["topic"]["id"] == topic["id"]
    assert result["topic"]["state"] == "inactive"

    result = runner.invoke(
        [
            "topic-update",
            topic["id"],
            "--etag",
            result["topic"]["etag"],
            "--name",
            "foobar",
        ]
    )

    assert result["topic"]["id"] == topic["id"]
    assert result["topic"]["state"] == "inactive"
    assert result["topic"]["name"] == "foobar"

    result = runner.invoke(
        ["topic-update", topic["id"], "--etag", result["topic"]["etag"], "--active"]
    )

    assert result["topic"]["state"] == "active"


def test_update_with_component_types(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    result = runner.invoke(
        [
            "topic-update",
            topic["id"],
            "--etag",
            topic["etag"],
            "--component_types",
            "foo,bar",
        ]
    )

    assert result["topic"]["id"] == topic["id"]
    assert len(result["topic"]["component_types"]) == 2
    assert result["topic"]["component_types"][0] == "foo"
    assert result["topic"]["component_types"][1] == "bar"


def test_update_with_data(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    result = runner.invoke(
        [
            "topic-update",
            topic["id"],
            "--etag",
            topic["etag"],
            "--data",
            '{"foo": "bar"}',
        ]
    )

    assert result["topic"]["id"] == topic["id"]
    assert result["topic"]["data"]["foo"] == "bar"


def test_update_export_control_no_change(runner, product_id):
    topic = runner.invoke(
        [
            "topic-create",
            "--name",
            "osp",
            "--product-id",
            product_id,
            "--export-control",
        ]
    )["topic"]
    result = runner.invoke(["topic-update", topic["id"], "--etag", topic["etag"]])
    assert result["topic"]["id"] == topic["id"]
    assert result["topic"]["export_control"] == topic["export_control"]


def test_update_no_export_control_no_change(runner, product_id):
    topic = runner.invoke(
        [
            "topic-create",
            "--name",
            "osp",
            "--product-id",
            product_id,
            "--no-export-control",
        ]
    )["topic"]
    result = runner.invoke(["topic-update", topic["id"], "--etag", topic["etag"]])
    assert result["topic"]["id"] == topic["id"]
    assert result["topic"]["export_control"] == topic["export_control"]


def test_update_export_control(runner, product_id):
    topic = runner.invoke(
        [
            "topic-create",
            "--name",
            "osp",
            "--product-id",
            product_id,
            "--export-control",
        ]
    )["topic"]
    result = runner.invoke(
        ["topic-update", topic["id"], "--etag", topic["etag"], "--no-export-control"]
    )
    assert result["topic"]["id"] == topic["id"]
    assert result["topic"]["export_control"] is False


def test_update_no_export_control(runner, product_id):
    topic = runner.invoke(
        [
            "topic-create",
            "--name",
            "osp",
            "--product-id",
            product_id,
            "--no-export-control",
        ]
    )["topic"]
    result = runner.invoke(
        ["topic-update", topic["id"], "--etag", topic["etag"], "--export-control"]
    )
    assert result["topic"]["id"] == topic["id"]
    assert result["topic"]["export_control"] is True


def test_where_on_list(runner, product_id):
    runner.invoke(["topic-create", "--name", "osp1", "--product-id", product_id])
    runner.invoke(["topic-create", "--name", "osp2", "--product-id", product_id])
    assert runner.invoke(["topic-list", "--where", "name:osp1"])["_meta"]["count"]
