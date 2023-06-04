# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Red Hat, Inc
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

from dciclient.v1.api import job as api_job


def test_add_remove_job_component(dci_context, job, component):
    r = api_job.add_component(
        dci_context, job["id"], component["id"]
    )
    assert r.status_code == 201
    r = api_job.get_components(dci_context, job["id"])
    assert r.status_code == 200
    cmpts = r.json()["components"]
    cmpt_found = False
    for c in cmpts:
        if c["id"] == component["id"]:
            cmpt_found = True
    assert cmpt_found
    r = api_job.remove_component(
        dci_context, job["id"], component["id"]
    )
    assert r.status_code == 201
    r = api_job.get_components(dci_context, job["id"])
    assert r.status_code == 200
    cmpts = r.json()["components"]
    cmpt_found = False
    for c in cmpts:
        if c["id"] == component["id"]:
            cmpt_found = True
    assert not cmpt_found
