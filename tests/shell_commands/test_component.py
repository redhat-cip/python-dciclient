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
            "--name",
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
            "--name",
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
            "--name",
            "foo",
            "--type",
            "foobar",
            "--topic-id",
            topic["id"],
            "--tags",
            "tag1,tag2",
            "--released-at",
            "2020-08-29T10:33:57.914078"
        ]
    )["component"]["id"]

    component = runner.invoke(
        [
            "component-show",
            component_id
        ]
    )["component"]

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
            "--name",
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
            "--name",
            "foo",
            "--type",
            "bar",
            "--topic-id",
            topic["id"],
        ]
    )["component"]

    result = runner.invoke_raw(
        ["component-delete",
         component["id"],
         "--etag", component["etag"]]
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
            "--name",
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
            "--name",
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
        ["component-file-delete", component["id"], "--file-id", new_f["id"], "--etag", new_f["etag"]]  # noqa
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
            "--name",
            "name",
            "--canonical_project_name",
            "canonical",
            "--type",
            "type",
            "--tags",
            "foo,bar",
            "--title",
            "title",
            "--message",
            "a message",
            "--url",
            "http://localhost/foo",
            "--topic-id",
            topic["id"],
        ]
    )["component"]

    assert component["name"] == "name"
    assert component["canonical_project_name"] == "canonical"
    assert component["type"] == "type"
    assert component["title"] == "title"
    assert component["message"] == "a message"
    assert component["url"] == "http://localhost/foo"
    assert len(component["tags"]) == 2
    assert component["tags"][0] == "foo"
    assert component["tags"][1] == "bar"

    result = runner.invoke(
        [
            "component-update",
            "--name",
            "newname",
            "--canonical_project_name",
            "newcanonical",
            "--type",
            "newtype",
            "--tags",
            "new,tag",
            "--title",
            "newtitle",
            "--message",
            "a new message",
            "--url",
            "http://localhost/bar",
            component["id"],
        ]
    )["component"]

    assert result["name"] == "newname"
    assert result["canonical_project_name"] == "newcanonical"
    assert result["type"] == "newtype"
    assert result["title"] == "newtitle"
    assert result["message"] == "a new message"
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
            "--name",
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
            "--name",
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
            "--name",
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
            "--name",
            "bar",
            "--type",
            "bar2",
            "--topic-id",
            topic["id"],
        ]
    )

    assert (
        len(runner.invoke(
            ["component-list", "--topic-id", topic["id"], "--where", "type:bar2"]
        )["components"])
        == 1
    )
