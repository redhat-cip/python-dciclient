# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from dciclient.v1.api import topic as api_topic


def test_get_or_create_topic(dci_context, product_id):
    nb_topics = len(api_topic.list(dci_context).json()["topics"])
    kwargs = {
        "name": "topic1",
        "component_types": ["type_1", "type_2"],
        "product_id": product_id,
        "export_control": False,
    }
    topic = api_topic.create(dci_context, **kwargs).json()["topic"]
    nb_topics += 1

    r = api_topic.get_or_create(
        dci_context,
        name="topic1",
        defaults={"product_id": product_id, "export_control": True},
    )
    assert r.status_code == 200
    existing_topic = r.json()["topic"]
    assert existing_topic["id"] == topic["id"]
    assert existing_topic["export_control"] is False

    r = api_topic.get_or_create(
        dci_context,
        name="topic2",
        defaults={"product_id": product_id, "export_control": True},
    )
    nb_topics += 1
    assert r.status_code == 201
    new_topic = r.json()["topic"]
    assert new_topic["id"] != topic["id"]
    assert new_topic["export_control"]

    assert len(api_topic.list(dci_context).json()["topics"]) == nb_topics
