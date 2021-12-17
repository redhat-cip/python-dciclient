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
import json
import os
import tempfile

from dciclient.v1.api import file as dci_file
from dciclient.v1.api import job


def test_iter(dci_context, job_id):
    f_names = ["file_%d" % i for i in range(100)]
    for name in f_names:
        dci_file.create(
            dci_context,
            name=name,
            content="some content",
            mime="plain/text",
            job_id=job_id,
        )
    cpt = 0
    seen_names = []
    for f in job.list_files_iter(dci_context, id=job_id, limit=200, offset=0):
        seen_names.append(f["name"])
        cpt += 1
    # job already comes with 2 files
    all_files = len(job.list_files(dci_context,
                                   id=job_id,
                                   limit=200,
                                   offset=0).json()["files"])
    assert all_files == 100 + 2
    assert cpt == 100 + 2
    assert len(set(seen_names) - set(f_names)) == 2


def test_nrt_file_upload_json_content(
    remoteci_id, remoteci_api_secret, signature_context_factory, job_id
):
    dci_context = signature_context_factory(
        client_id=remoteci_id, api_secret=remoteci_api_secret
    )
    r = dci_file.create(
        dci_context,
        name="dci.json",
        content=json.dumps({"inventory_file": "/etc/dci-openshift-agent/hosts"}),
        mime="application/json",
        job_id=job_id,
    )
    assert r.status_code == 201


def test_nrt_file_upload_json_file(
    remoteci_id, remoteci_api_secret, signature_context_factory, job_id
):
    dci_context = signature_context_factory(
        client_id=remoteci_id, api_secret=remoteci_api_secret
    )
    test_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(test_dir, "data", "dci.json")
    r = dci_file.create(
        dci_context,
        name="dci.json",
        file_path=json_file_path,
        mime="application/json",
        job_id=job_id,
    )
    assert r.status_code == 201


def test_nrt_file_upload_targz_file(
    remoteci_id, remoteci_api_secret, signature_context_factory, job_id
):
    dci_context = signature_context_factory(
        client_id=remoteci_id, api_secret=remoteci_api_secret
    )
    test_dir = os.path.dirname(os.path.abspath(__file__))
    tgz_file_path = os.path.join(test_dir, "data", "dci.tgz")
    r = dci_file.create(
        dci_context,
        name="dci.tgz",
        file_path=tgz_file_path,
        mime="application/octet-stream",
        job_id=job_id,
    )
    assert r.status_code == 201


def test_nrt_file_upload_empty_file(
    remoteci_id, remoteci_api_secret, signature_context_factory, job_id
):
    dci_context = signature_context_factory(
        client_id=remoteci_id, api_secret=remoteci_api_secret
    )
    empty_file_fd, empty_file_path = tempfile.mkstemp()

    try:
        r = dci_file.create(
            dci_context,
            name="empty.txt",
            file_path=empty_file_path,
            mime="text/plain",
            job_id=job_id,
        )
        assert r.status_code == 201

        f = dci_file.get(dci_context, r.json()["file"]["id"]).json()["file"]
        assert f["name"] == "empty.txt"
        assert f["size"] == 0
    except Exception as e:
        raise e
    finally:
        os.close(empty_file_fd)
        os.remove(empty_file_path)


def test_nrt_file_upload_empty_content_string(
    remoteci_id, remoteci_api_secret, signature_context_factory, job_id
):
    dci_context = signature_context_factory(
        client_id=remoteci_id, api_secret=remoteci_api_secret
    )

    r = dci_file.create(
        dci_context,
        name="empty_string.txt",
        content="",
        mime="text/plain",
        job_id=job_id,
    )
    assert r.status_code == 201

    f = dci_file.get(dci_context, r.json()["file"]["id"]).json()["file"]
    assert f["name"] == "empty_string.txt"
    assert f["size"] == 0
