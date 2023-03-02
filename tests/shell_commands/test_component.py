# -*- encoding: utf-8 -*-
#
# Copyright 2015-2022 Red Hat, Inc.
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
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    teams = runner.invoke(["team-list"])["teams"]
    team_id = teams[0]["id"]

    runner.invoke(["topic-attach-team", topic["id"], "--team-id", team_id])

    runner.invoke(
        [
            "component-create",
            "foo",
            "--type",
            "bar",
            "--topic-id",
            topic["id"],
        ]
    )
    runner.invoke(
        [
            "component-create",
            "bar",
            "--type",
            "bar2",
            "--topic-id",
            topic["id"],
        ]
    )
    components = runner.invoke(["component-list", "--topic-id", topic["id"]])[
        "components"
    ]

    assert len(components) == 2
    assert components[0]["name"] == "bar"
    assert components[1]["name"] == "foo"


def test_create(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]

    component_id = runner.invoke(
        [
            "component-create",
            "foo",
            "--type",
            "foobar",
            "--topic-id",
            topic["id"],
            "--tags",
            "tag1,tag2",
            "--released-at",
            "2020-08-29T10:33:57.914078",
        ]
    )["component"]["id"]

    component = runner.invoke(["component-show", component_id])["component"]

    assert component["name"] == "foo"
    assert component["tags"] == ["tag1", "tag2"]
    assert component["released_at"] == "2020-08-29T10:33:57.914078"


def test_create_inactive(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]

    component = runner.invoke(
        [
            "component-create",
            "foo",
            "--type",
            "foobar",
            "--topic-id",
            topic["id"],
            "--no-active",
        ]
    )["component"]
    assert component["state"] == "inactive"


def test_delete(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    component = runner.invoke(
        [
            "component-create",
            "foo",
            "--type",
            "bar",
            "--topic-id",
            topic["id"],
        ]
    )["component"]

    result = runner.invoke_raw(
        ["component-delete", component["id"], "--etag", component["etag"]]
    )

    assert result.status_code == 204


def test_show(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    assert topic["name"] == "osp"

    component = runner.invoke(
        [
            "component-create",
            "foo",
            "--type",
            "bar",
            "--topic-id",
            topic["id"],
        ]
    )["component"]

    result = runner.invoke(["component-show", component["id"]])

    assert result["component"]["name"] == "foo"


def test_file_support(runner, tmpdir, product_id):
    td = tmpdir
    p = td.join("hello.txt")
    p.write("content")
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]

    component = runner.invoke(
        [
            "component-create",
            "foo",
            "--type",
            "foobar",
            "--topic-id",
            topic["id"],
        ]
    )["component"]

    # upload
    new_f = runner.invoke(
        ["component-file-upload", component["id"], "--path", p.strpath]
    )["component_file"]
    assert new_f["size"] == 7

    # show
    new_f = runner.invoke(
        ["component-file-show", component["id"], "--file-id", new_f["id"]]
    )["component_file"]
    assert new_f["size"] == 7

    # download
    runner.invoke_raw(
        [
            "component-file-download",
            component["id"],
            "--file-id",
            new_f["id"],
            "--target",
            td.strpath + "/my_file",
        ]
    )
    assert open(td.strpath + "/my_file", "r").read() == "content"

    # list
    my_list = runner.invoke(["component-file-list", component["id"]])["component_files"]
    assert len(my_list) == 1
    assert my_list[0]["size"] == 7

    # delete
    runner.invoke_raw(
        [
            "component-file-delete",
            component["id"],
            "--file-id",
            new_f["id"],
            "--etag",
            new_f["etag"],
        ]
    )
    result = runner.invoke_raw(
        ["component-file-show", component["id"], "--file-id", new_f["id"]]
    )
    assert result.status_code == 404


def test_update(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]

    component = runner.invoke(
        [
            "component-create",
            "name",
            "--type",
            "type",
            "--tags",
            "foo,bar",
            "--url",
            "http://localhost/foo",
            "--topic-id",
            topic["id"],
            "--version",
            "v1.2.3",
        ]
    )["component"]

    assert component["display_name"] == "name"
    assert component["version"] == "v1.2.3"
    assert component["type"] == "type"
    assert component["url"] == "http://localhost/foo"
    assert len(component["tags"]) == 2
    assert component["tags"][0] == "foo"
    assert component["tags"][1] == "bar"

    result = runner.invoke(
        [
            "component-update",
            component["id"],
            "--display-name",
            "newname",
            "--type",
            "newtype",
            "--tags",
            "new,tag",
            "--url",
            "http://localhost/bar",
            "--version",
            "v2.0.0",
        ]
    )["component"]

    assert result["display_name"] == "newname"
    assert result["version"] == "v2.0.0"
    assert result["type"] == "newtype"
    assert result["url"] == "http://localhost/bar"
    assert len(result["tags"]) == 2
    assert result["tags"][0] == "new"
    assert result["tags"][1] == "tag"


def test_update_with_data(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]

    component = runner.invoke(
        [
            "component-create",
            "foo",
            "--type",
            "bar",
            "--topic-id",
            topic["id"],
        ]
    )["component"]

    assert len(component["data"]) == 0

    result = runner.invoke(
        [
            "component-update",
            component["id"],
            "--data",
            '{"foo": "bar"}',
        ]
    )

    assert result["component"]["data"]["foo"] == "bar"


def test_update_active(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]

    component = runner.invoke(
        [
            "component-create",
            "foo",
            "--type",
            "bar",
            "--topic-id",
            topic["id"],
        ]
    )["component"]

    assert component["state"] == "active"

    result = runner.invoke(["component-update", component["id"], "--no-active"])
    assert result["component"]["state"] == "inactive"

    result = runner.invoke(["component-update", component["id"], "--active"])
    assert result["component"]["state"] == "active"


def test_where_on_list(runner, product_id):
    topic = runner.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    teams = runner.invoke(["team-list"])["teams"]
    team_id = teams[0]["id"]

    runner.invoke(["topic-attach-team", topic["id"], "--team-id", team_id])

    runner.invoke(
        [
            "component-create",
            "foo",
            "--type",
            "bar",
            "--topic-id",
            topic["id"],
        ]
    )
    runner.invoke(
        [
            "component-create",
            "bar",
            "--type",
            "bar2",
            "--topic-id",
            topic["id"],
        ]
    )

    assert (
        len(
            runner.invoke(
                ["component-list", "--topic-id", topic["id"], "--where", "type:bar2"]
            )["components"]
        )
        == 1
    )

    assert (
        len(
            runner.invoke(
                [
                    "component-list",
                    "--topic-id",
                    topic["id"],
                    "--query",
                    "eq(type,bar2)",
                ]
            )["components"]
        )
        == 1
    )


def test_create_component(runner, topic, team_user_name, team_user_id):
    component = runner.invoke_create_component(
        [
            "--url",
            "https://company.com/product/",
            "--tags",
            "tag1,tag2",
            '--data={"toto": false}',
            "--team",
            team_user_name,
            topic,
            "My Company Product",
            "v1.0",
            "ga",
        ]
    )["component"]
    assert component["tags"] == ["tag1", "tag2", "build:ga"]
    assert component["type"] == "my-company-product"
    assert component["display_name"] == "My Company Product v1.0"
    assert component["version"] == "v1.0"
    assert component["url"] == "https://company.com/product/"
    assert component["data"] == {"toto": False}
    assert component["team_id"] == team_user_id


def test_find_latest_component(runner, product, component):
    comp = runner.invoke_find_latest_component(
        ["--tags", ",".join(component["tags"]), product["name"], component["type"]]
    )
    assert comp["id"] == component["id"]
    assert comp["type"] == component["type"]
