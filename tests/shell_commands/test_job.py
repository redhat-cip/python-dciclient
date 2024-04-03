# -*- encoding: utf-8 -*-
#
# Copyright 2015-2024 Red Hat, Inc.
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

from dciclient.v1.api import job

import pytest
import requests
import requests.exceptions


try:
    requests.get("http://google.com")
except requests.exceptions.ConnectionError:
    internet_cnx = False
else:
    internet_cnx = True


def test_list(
    runner,
    dci_context,
    dci_context_remoteci,
    remoteci_id,
    product_id,
):
    topic = runner.invoke(
        [
            "topic-create",
            "--name",
            "osp",
            "--component_types",
            "type_1",
            "--export-control",
            "--product-id",
            product_id,
        ]
    )["topic"]

    runner.invoke(
        [
            "component-create",
            "foo",
            "--type",
            "type_1",
            "--topic-id",
            topic["id"],
        ]
    )["component"]

    job.schedule(dci_context_remoteci, topic["id"])
    l_job = runner.invoke(["job-list"])
    assert len(l_job["jobs"]) == 1
    assert l_job["jobs"][0]["remoteci"]["id"] == remoteci_id
    assert l_job["jobs"][0]["topic"]["id"] == topic["id"]
    output = runner.invoke(["job-list"])
    assert output["jobs"][0]["topic"]["name"] == "osp"
    assert output["jobs"][0]["id"] == l_job["jobs"][0]["id"]

    l_job = runner.invoke(["job-list", "--where", "remoteci_id:" + remoteci_id])
    assert len(l_job["jobs"]) == 1

    l_job = runner.invoke(["job-list", "--query", "eq(remoteci_id,%s)" % remoteci_id])
    assert len(l_job["jobs"]) == 1


def test_list_as_remoteci(job, remoteci_id, runner_remoteci):
    l_job = runner_remoteci.invoke(["job-list"])
    assert len(l_job["jobs"]) == 1
    assert l_job["jobs"][0]["remoteci"]["id"] == remoteci_id
    assert l_job["jobs"][0]["topic"]["id"] == job["topic_id"]
    output = runner_remoteci.invoke(["job-list"])
    assert output["jobs"][0]["topic"]["name"] == "foo_topic"
    assert output["jobs"][0]["id"] == job["id"]

    l_job = runner_remoteci.invoke(
        ["job-list", "--where", "remoteci_id:" + remoteci_id]
    )
    assert len(l_job["jobs"]) == 1

    l_job = runner_remoteci.invoke(
        ["job-list", "--query", "eq(remoteci_id,%s)" % remoteci_id]
    )
    assert len(l_job["jobs"]) == 1


def test_list_with_limit(runner, job_factory):
    for _ in range(6):
        job_factory()
    # test --limit XX
    l_job = runner.invoke(["job-list"])
    assert len(l_job["jobs"]) == 6
    l_job = runner.invoke(["job-list", "--limit", "1"])
    assert len(l_job["jobs"]) == 1


def test_delete(runner, job_id):
    l_job = runner.invoke(["job-show", job_id])
    l_job_etag = l_job["job"]["etag"]

    result = runner.invoke_raw(["job-delete", job_id, "--etag", l_job_etag])

    assert result.status_code == 204


def test_update(runner, job_id):
    l_job = runner.invoke(["job-update", job_id])
    result = runner.invoke_raw(
        ["job-update", job_id, "--status_reason", "new-status-reason"]
    )
    assert result.status_code == 200

    l_job = runner.invoke(["job-show", job_id])
    assert l_job["job"]["status_reason"] == "new-status-reason"


def test_results(runner, job_id):
    result = runner.invoke(["job-results", job_id])["results"][0]

    assert result["filename"] == "res_junit.xml"


def test_job_output(runner, job_id):
    result = runner.invoke_raw(["job-output", job_id])
    assert result[0].startswith("pre-run")


def test_file_support(runner, tmpdir, job_id):
    td = tmpdir
    p = td.join("hello.txt")
    p.write("content")

    # upload
    new_f = runner.invoke(
        [
            "job-upload-file",
            job_id,
            "--name",
            "test",
            "--mime",
            "application/octet-stream",
            "--path",
            p.strpath,
        ]
    )["file"]
    assert new_f["size"] == 7

    # show
    new_f = runner.invoke(["file-show", new_f["id"]])["file"]
    assert new_f["size"] == 7
    assert new_f["mime"] == "application/octet-stream"

    # download
    runner.invoke_raw(
        [
            "job-download-file",
            job_id,
            "--file-id",
            new_f["id"],
            "--target",
            td.strpath + "/my_file",
        ]
    )
    assert open(td.strpath + "/my_file", "r").read() == "content"

    # list
    my_list = runner.invoke(["job-list-file", job_id])["files"]
    assert len(my_list) == 3
    assert my_list[0]["size"] == 7

    # delete
    runner.invoke_raw(["file-delete", new_f["id"]])
    result = runner.invoke_raw(["file-show", new_f["id"]])
    assert result.status_code == 404


def test_file_support_as_remoteci(runner_remoteci, tmpdir, job_id):
    td = tmpdir
    p = td.join("remoteci.txt")
    content = u"remoteci content".encode("utf-8")
    p.write(content, "wb")

    my_original_list = runner_remoteci.invoke(["job-list-file", job_id])["files"]

    # upload
    new_f = runner_remoteci.invoke(
        ["job-upload-file", job_id, "--name", "testrci", "--path", p.strpath]
    )["file"]
    assert new_f["size"] == len(content)

    # show
    new_f = runner_remoteci.invoke(["file-show", new_f["id"]])["file"]
    assert new_f["size"] == len(content)

    # download
    runner_remoteci.invoke_raw(
        [
            "job-download-file",
            job_id,
            "--file-id",
            new_f["id"],
            "--target",
            td.strpath + "/my_file",
        ]
    )
    assert open(td.strpath + "/my_file", "rb").read() == content

    # list
    my_list = runner_remoteci.invoke(["job-list-file", job_id])["files"]
    assert len(my_list) == len(my_original_list) + 1
    assert my_list[0]["size"] == len(content)

    # delete
    runner_remoteci.invoke_raw(["file-delete", new_f["id"]])
    result = runner_remoteci.invoke_raw(["file-show", new_f["id"]])
    assert result.status_code == 404


def test_diff_jobs(runner, job_id):
    result = runner.invoke_diff_jobs(["--job_id_1", job_id, "--job_id_2", job_id])
    assert result == []


def test_diff_jobs_invalid_parameter(runner, job_id):
    with pytest.raises(requests.models.JSONDecodeError):
        runner.invoke_diff_jobs(["--job_id_1", "toto"])


def test_job_key_value(runner, job_id):
    runner.invoke(["job-add-key-value", job_id, "key_1", "123.123"])
    j = runner.invoke(["job-show", job_id])["job"]
    assert j["keys_values"][0]["key"] == "key_1"
    assert j["keys_values"][0]["value"] == 123.123

    runner.invoke(["job-delete-key-value", job_id, "key_1"])
    j = runner.invoke(["job-show", job_id])["job"]


def test_create_job(runner_remoteci, topic, topic_id, job_id, component, remoteci_id):
    url = "https://company.com/ci/job/42"
    job = runner_remoteci.invoke_create_job(
        [
            "--url", url,
            "--tag", "tag1",
            "--tag", "tag2",
            "--topic", topic,
            "--name", "my-job",
            "--comment", "comment",
            "--comp", component["name"],
            "--remoteci", "remoteci",
            "--key-value", "key=42",
            "--data", '{"jenkins_url": "https://jenkins.corp.com/job/name/42"}',
            "--previous-job-id", job_id,
        ]
    )["job"]
    assert job["tags"] == ["tag1", "tag2"]
    assert job["url"] == url
    assert job["comment"] == "comment"
    assert job["name"] == "my-job"
    assert job["keys_values"][0]["key"] == "key"
    assert job["keys_values"][0]["value"] == 42.0
    assert job["components"][0]["id"] == component["id"]
    assert job["topic_id"] == topic_id
    assert job["remoteci_id"] == remoteci_id
    assert job["data"]["jenkins_url"] == "https://jenkins.corp.com/job/name/42"
    assert job["previous_job_id"] == job_id
