# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2022 Red Hat, Inc
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

from dciclient.v1.api import component as api_component
from dciclient.v1.api import topic as api_topic


def test_success_download_component_file_returns_http_response(
    dci_context, component_id, tmpdir
):
    """Ensure an http response is retrieved."""

    tmp_file = tmpdir.mkdir("data").join("content")
    tmp_file.write("DISTRIBUTED-CI")

    api_component.file_upload(dci_context, component_id, tmp_file.strpath)

    file_id = api_component.file_list(dci_context, component_id).json()[
        "component_files"
    ][0]["id"]

    res = api_component.file_download(
        dci_context, component_id, file_id, tmp_file.strpath
    )

    assert res is None


def test_add_tags_with_an_update(dci_context, component):
    r = api_component.update(
        dci_context, component["id"], etag=component["etag"], tags=["t1", "t2"]
    )
    assert r.status_code == 200
    assert "t1" in r.json()["component"]["tags"]
    assert "t2" in r.json()["component"]["tags"]
    etag = r.json()["component"]["etag"]
    r = api_component.update(dci_context, component["id"], etag=etag)
    assert r.status_code == 200
    assert "t1" in r.json()["component"]["tags"]
    assert "t2" in r.json()["component"]["tags"]


def test_add_tag(dci_context, component):
    r = api_component.add_tag(dci_context, component["id"], "tag 1")
    assert r.status_code == 200
    assert "tag 1" in r.json()["component"]["tags"]
    r = api_component.add_tag(dci_context, component["id"], "tag 2")
    assert r.status_code == 200
    assert "tag 2" in r.json()["component"]["tags"]


def test_delete_tags(dci_context, component_id):
    r = api_component.add_tag(dci_context, component_id, "tag 1")
    r = api_component.add_tag(dci_context, component_id, "tag 2")
    assert "tag 1" in r.json()["component"]["tags"]
    assert "tag 2" in r.json()["component"]["tags"]
    r = api_component.delete_tag(dci_context, component_id, "tag 1")
    assert r.status_code == 200
    assert "tag 1" not in r.json()["component"]["tags"]
    r = api_component.delete_tag(dci_context, component_id, "tag 2")
    assert r.status_code == 200
    assert "tag 2" not in r.json()["component"]["tags"]
    r = api_component.delete_tag(dci_context, component_id, "tag 2")
    assert r.status_code == 200


def test_get_or_create_component(dci_context, topic_id):
    nb_components = len(
        api_topic.list_components(dci_context, topic_id).json()["components"]
    )
    component = {
        "name": "component1",
        "type": "component_type",
        "data": {"dir": "/tmp"},
        "topic_id": topic_id,
    }
    component = api_component.create(dci_context, **component).json()["component"]
    nb_components += 1

    r, created = api_component.get_or_create(
        dci_context,
        name="component1",
        topic_id=topic_id,
        type="component_type",
        defaults={"canonical_project_name": "canonical component1"},
    )
    assert r.status_code == 200
    assert created is False
    existing_component = r.json()["component"]
    assert existing_component["id"] == component["id"]
    assert existing_component["canonical_project_name"] is None

    r, created = api_component.get_or_create(
        dci_context,
        name="component2",
        topic_id=topic_id,
        type="component_type",
        defaults={"canonical_project_name": "canonical component2"},
    )
    assert created
    nb_components += 1
    assert r.status_code == 201
    new_component = r.json()["component"]
    assert new_component["id"] != component["id"]
    assert new_component["canonical_project_name"] == "canonical component2"

    assert (
        len(api_topic.list_components(dci_context, topic_id).json()["components"])
        == nb_components
    )
