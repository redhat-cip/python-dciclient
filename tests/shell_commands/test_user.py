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


def test_create_user(runner, test_user, team_user_id):
    assert test_user["name"] == "foo"
    assert test_user["fullname"] == "Foo Bar"
    assert test_user["email"] == "foo@example.org"
    assert test_user["team_id"] == team_user_id


def test_create_admin(runner, team_id):
    user = runner.invoke(
        [
            "user-create",
            "--name",
            "foo",
            "--email",
            "foo@example.org",
            "--password",
            "pass",
            "--team-id",
            team_id,
        ]
    )["user"]
    assert user["name"] == "foo"
    assert user["fullname"] == "foo"
    assert user["email"] == "foo@example.org"
    assert user["team_id"] == team_id


def test_create_super_admin(runner, team_id):
    user = runner.invoke(
        [
            "user-create",
            "--name",
            "foo",
            "--email",
            "foo@example.org",
            "--password",
            "pass",
            "--team-id",
            team_id,
        ]
    )["user"]
    assert user["name"] == "foo"
    assert user["fullname"] == "foo"
    assert user["email"] == "foo@example.org"
    assert user["team_id"] == team_id


def test_create_inactive(runner, team_id):
    user = runner.invoke(
        [
            "user-create",
            "--name",
            "foo",
            "--password",
            "pass",
            "--email",
            "foo@example.org",
            "--team-id",
            team_id,
            "--no-active",
        ]
    )["user"]
    assert user["state"] == "inactive"


def test_list(runner, team_id):
    users_cnt = len(runner.invoke(["user-list"])["users"])
    runner.invoke(
        [
            "user-create",
            "--name",
            "bar",
            "--email",
            "bar@example.org",
            "--password",
            "pass",
            "--team-id",
            team_id,
        ]
    )
    new_users_cnt = len(runner.invoke(["user-list"])["users"])
    assert new_users_cnt == users_cnt + 1


def test_update(runner, test_user):
    runner.invoke(
        [
            "user-update",
            test_user["id"],
            "--etag",
            test_user["etag"],
            "--name",
            "bar",
            "--email",
            "bar@example.org",
            "--fullname",
            "Barry White",
        ]
    )
    user = runner.invoke(["user-show", test_user["id"]])["user"]

    assert user["name"] == "bar"
    assert user["fullname"] == "Barry White"
    assert user["email"] == "bar@example.org"


def test_update_team_id(runner, test_user, team_user_id, team_id):
    user = runner.invoke(["user-show", test_user["id"]])["user"]
    assert user["team_id"] == team_user_id

    runner.invoke(
        [
            "user-update",
            test_user["id"],
            "--etag",
            test_user["etag"],
            "--team-id",
            team_id,
        ]
    )
    user = runner.invoke(["user-show", test_user["id"]])["user"]
    assert user["team_id"] == team_id


def test_update_active(runner, test_user, team_id):
    assert test_user["state"] == "active"

    result = runner.invoke(
        ["user-update", test_user["id"], "--etag", test_user["etag"], "--no-active"]
    )

    assert result["user"]["id"] == test_user["id"]
    assert result["user"]["state"] == "inactive"

    result = runner.invoke(
        [
            "user-update",
            test_user["id"],
            "--etag",
            result["user"]["etag"],
            "--name",
            "foobar",
        ]
    )

    assert result["user"]["id"] == test_user["id"]
    assert result["user"]["state"] == "inactive"
    assert result["user"]["name"] == "foobar"

    result = runner.invoke(
        ["user-update", test_user["id"], "--etag", result["user"]["etag"], "--active"]
    )

    assert result["user"]["state"] == "active"


def test_delete(runner, test_user, team_id):
    result = runner.invoke_raw(
        ["user-delete", test_user["id"], "--etag", test_user["etag"]]
    )
    assert result.status_code == 204


def test_show(runner, test_user, team_id):
    user = runner.invoke(["user-show", test_user["id"]])["user"]

    assert user["name"] == test_user["name"]


def test_where_on_list(runner, test_user, team_id):
    runner.invoke(
        [
            "user-create",
            "--name",
            "foo2",
            "--email",
            "foo2@example.org",
            "--password",
            "pass",
            "--team-id",
            team_id,
        ]
    )
    runner.invoke(
        [
            "user-create",
            "--name",
            "foo3",
            "--email",
            "foo3@example.org",
            "--password",
            "pass",
            "--team-id",
            team_id,
        ]
    )
    users_cnt = len(runner.invoke(["user-list"])["users"])
    assert runner.invoke(["user-list"])["_meta"]["count"] == users_cnt
    assert runner.invoke(["user-list", "--where", "name:foo"])["_meta"]["count"] == 1
