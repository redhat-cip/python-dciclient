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


def test_list(toto_context, product_id):
    topic = toto_context.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    teams = toto_context.invoke(["team-list"])["teams"]
    team_id = teams[0]["id"]

    toto_context.invoke(["topic-attach-team", topic["id"], "--team-id", team_id])

    toto_context.invoke(
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
    toto_context.invoke(
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
    components = toto_context.invoke(["component-list", "--topic-id", topic["id"]])[
        "components"
    ]

    assert len(components) == 2
    assert components[0]["name"] == "bar"
    assert components[1]["name"] == "foo"


def test_create(toto_context, product_id):
    topic = toto_context.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]

    component = toto_context.invoke(
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
    assert component["name"] == "foo"


def test_create_inactive(toto_context, product_id):
    topic = toto_context.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]

    component = toto_context.invoke(
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


def test_delete(toto_context, product_id):
    topic = toto_context.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    component = toto_context.invoke(
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

    result = toto_context.invoke_raw(["component-delete", component["id"]])

    assert result.status_code == 204


def test_show(toto_context, product_id):
    topic = toto_context.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    assert topic["name"] == "osp"

    component = toto_context.invoke(
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

    result = toto_context.invoke(["component-show", component["id"]])

    assert result["component"]["name"] == "foo"


def test_file_support(toto_context, tmpdir, product_id):
    td = tmpdir
    p = td.join("hello.txt")
    p.write("content")
    topic = toto_context.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]

    component = toto_context.invoke(
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
    new_f = toto_context.invoke(
        ["component-file-upload", component["id"], "--path", p.strpath]
    )["component_file"]
    assert new_f["size"] == 7

    # show
    new_f = toto_context.invoke(
        ["component-file-show", component["id"], "--file-id", new_f["id"]]
    )["component_file"]
    assert new_f["size"] == 7

    # download
    toto_context.invoke_raw(
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
    my_list = toto_context.invoke(["component-file-list", component["id"]])[
        "component_files"
    ]
    assert len(my_list) == 1
    assert my_list[0]["size"] == 7

    # delete
    toto_context.invoke_raw(
        ["component-file-delete", component["id"], "--file-id", new_f["id"]]
    )
    result = toto_context.invoke(
        ["component-file-show", component["id"], "--file-id", new_f["id"]]
    )
    assert result["status_code"] == 404


def test_update_active(toto_context, product_id):
    topic = toto_context.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]

    component = toto_context.invoke(
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

    result = toto_context.invoke(["component-update", component["id"], "--no-active"])
    assert result["component"]["state"] == "inactive"

    result = toto_context.invoke(["component-update", component["id"], "--active"])
    assert result["component"]["state"] == "active"


def test_where_on_list(toto_context, product_id):
    topic = toto_context.invoke(
        ["topic-create", "--name", "osp", "--product-id", product_id]
    )["topic"]
    teams = toto_context.invoke(["team-list"])["teams"]
    team_id = teams[0]["id"]

    toto_context.invoke(["topic-attach-team", topic["id"], "--team-id", team_id])

    toto_context.invoke(
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
    toto_context.invoke(
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
        toto_context.invoke(
            ["component-list", "--topic-id", topic["id"], "--where", "type:bar2"]
        )["_meta"]["count"]
        == 1
    )
