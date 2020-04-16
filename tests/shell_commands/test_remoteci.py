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

from dciclient.v1.api import remoteci
from dciclient.v1.api import team

import mock


def test_list(toto_context):
    team = toto_context.invoke(["team-create", "--name", "foo"])["team"]
    toto_context.invoke(["remoteci-create", "--name", "foo", "--team-id", team["id"]])
    toto_context.invoke(["remoteci-create", "--name", "bar", "--team-id", team["id"]])
    remotecis = toto_context.invoke(["remoteci-list"])["remotecis"]

    assert len(remotecis) == 2
    assert remotecis[0]["name"] == "bar"
    assert remotecis[1]["name"] == "foo"


def test_create(toto_context):
    team = toto_context.invoke(["team-create", "--name", "foo"])["team"]
    remoteci = toto_context.invoke(
        ["remoteci-create", "--name", "foo", "--team-id", team["id"]]
    )["remoteci"]
    assert remoteci["name"] == "foo"
    assert remoteci["state"] == "active"


def test_create_inactive(toto_context):
    team = toto_context.invoke(["team-create", "--name", "foo"])["team"]
    remoteci = toto_context.invoke(
        ["remoteci-create", "--name", "foo", "--team-id", team["id"], "--no-active"]
    )["remoteci"]
    assert remoteci["state"] == "inactive"


def test_update(toto_context):
    team = toto_context.invoke(["team-create", "--name", "foo"])["team"]
    remoteci = toto_context.invoke(
        ["remoteci-create", "--name", "foo", "--team-id", team["id"]]
    )["remoteci"]

    result = toto_context.invoke(
        [
            "remoteci-update",
            remoteci["id"],
            "--etag",
            remoteci["etag"],
            "--name",
            "bar",
            "--no-active",
        ]
    )

    assert result["remoteci"]["id"] == remoteci["id"]
    assert result["remoteci"]["name"] == "bar"


def test_update_active(toto_context):
    team = toto_context.invoke(["team-create", "--name", "foo"])["team"]
    remoteci = toto_context.invoke(
        ["remoteci-create", "--name", "foo", "--team-id", team["id"]]
    )["remoteci"]

    assert remoteci["state"] == "active"

    result = toto_context.invoke(
        ["remoteci-update", remoteci["id"], "--etag", remoteci["etag"], "--no-active"]
    )

    assert result["remoteci"]["id"] == remoteci["id"]
    assert result["remoteci"]["state"] == "inactive"

    result = toto_context.invoke(
        [
            "remoteci-update",
            remoteci["id"],
            "--etag",
            result["remoteci"]["etag"],
            "--name",
            "foobar",
        ]
    )

    assert result["remoteci"]["id"] == remoteci["id"]
    assert result["remoteci"]["state"] == "inactive"

    result = toto_context.invoke(
        [
            "remoteci-update",
            remoteci["id"],
            "--etag",
            result["remoteci"]["etag"],
            "--active",
        ]
    )

    assert result["remoteci"]["state"] == "active"


def test_delete(toto_context):
    team = toto_context.invoke(["team-create", "--name", "foo"])["team"]

    remoteci = toto_context.invoke(
        ["remoteci-create", "--name", "foo", "--team-id", team["id"]]
    )["remoteci"]

    result = toto_context.invoke_raw(
        ["remoteci-delete", remoteci["id"], "--etag", remoteci["etag"]]
    )

    assert result.status_code == 204


def test_show(toto_context):
    team = toto_context.invoke(["team-create", "--name", "foo"])["team"]
    remoteci = toto_context.invoke(
        ["remoteci-create", "--name", "foo", "--team-id", team["id"]]
    )["remoteci"]

    remoteci = toto_context.invoke(["remoteci-show", remoteci["id"]])["remoteci"]

    assert remoteci["name"] == "foo"


def test_get_data(toto_context):
    team = toto_context.invoke(["team-create", "--name", "foo"])["team"]
    remoteci = toto_context.invoke(
        ["remoteci-create", "--name", "foo", "--team-id", team["id"]]
    )["remoteci"]

    result = toto_context.invoke(["remoteci-get-data", remoteci["id"]])
    assert result == {}
    toto_context.invoke(
        [
            "remoteci-update",
            remoteci["id"],
            "--etag",
            remoteci["etag"],
            "--data",
            '{"foo": "bar"}',
        ]
    )
    result = toto_context.invoke(["remoteci-get-data", remoteci["id"]])
    assert result == {"foo": "bar"}


def test_get_data_missing_key(toto_context):
    team = toto_context.invoke(["team-create", "--name", "foo"])["team"]
    remoteci = toto_context.invoke(
        ["remoteci-create", "--name", "foo", "--team-id", team["id"]]
    )["remoteci"]

    result = toto_context.invoke(
        ["remoteci-get-data", remoteci["id"], "--keys", "missing"]
    )
    assert result == {}


def test_embed(dci_context):
    team_id = team.create(dci_context, name="teama").json()["team"]["id"]

    rci = remoteci.create(dci_context, name="boa", team_id=team_id).json()
    rci_id = rci["remoteci"]["id"]

    rci_with_embed = remoteci.get(dci_context, id=rci_id, embed="team").json()
    embed_team_id = rci_with_embed["remoteci"]["team"]["id"]

    assert team_id == embed_team_id


def test_where_on_list(toto_context, team_id):
    toto_context.invoke(["remoteci-create", "--name", "bar1", "--team-id", team_id])
    toto_context.invoke(["remoteci-create", "--name", "bar2", "--team-id", team_id])
    assert (
        toto_context.invoke(["remoteci-list", "--where", "name:bar1"])["_meta"]["count"]
        == 1
    )


def test_refresh_remoteci_keys(toto_context, remoteci_id):
    with mock.patch("requests.sessions.Session.put") as post_mock:
        post_mock.return_value = '{"key": "XXX", "cert": "XXX" }'
        toto_context.invoke_raw(["remoteci-refresh-keys", remoteci_id, "--etag", "XX"])
        url = "http://dciserver.com/api/v1/remotecis/%s/keys" % remoteci_id
        post_mock.assert_called_once_with(
            url, headers={"If-match": "XX"}, json={}, timeout=600
        )
