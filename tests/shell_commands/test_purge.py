# -*- encoding: utf-8 -*-
#
# Copyright 2015-2017 Red Hat, Inc.
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


def test_purge_wrong_resource(toto_context):
    result = toto_context.invoke_raw(
        ["purge", "--force", "--resource", "wrongresource"]
    )
    assert "Unkown resource have been specified:" in result
    assert "wrongresource" in result


def test_purge_success_authorized_admin(toto_context):
    result = toto_context.invoke_raw(["purge"])
    assert result == {}


def test_purge_fail_unauthorized_user(toto_context_user):
    result = toto_context_user.invoke_raw(["purge"])
    assert result.status_code == 401


def test_purge_fail_unauthorized_user_admin(toto_context_user_admin):
    result = toto_context_user_admin.invoke_raw(["purge"])
    assert result.status_code == 401


def test_purge_noop(toto_context, remoteci_id, product_id):
    toto_context.invoke(["topic-create", "--name", "osp", "--product-id", product_id])
    toto_context.invoke(["topic-create", "--name", "osp2", "--product-id", product_id])
    topics = toto_context.invoke(["topic-list"])["topics"]
    topic_id = topics[0]["id"]
    assert len(topics) == 2

    toto_context.invoke_raw(["topic-delete", topic_id])
    topics = toto_context.invoke(["topic-list"])["topics"]
    assert len(topics) == 1

    purge_res = toto_context.invoke_raw(["purge", "--resource", "topics"])
    assert purge_res["topics"]["topics"][0]["id"] == topic_id
    assert purge_res["topics"]["topics"][0]["state"] == "archived"

    toto_context.invoke_raw(["purge", "--resource", "topics", "--force"])

    purge_res = toto_context.invoke_raw(["purge", "--resource", "topics"])
    assert len(purge_res) == 0

    topics = toto_context.invoke(["topic-list"])["topics"]
    assert len(topics) == 1
