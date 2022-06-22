# -*- encoding: utf-8 -*-
#
# Copyright Red Hat, Inc.
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


def test_create_and_show_pipeline(runner, team_user_id):
    p = runner.invoke(
        ["pipeline-create", "--name", "my-pipeline", "--team-id", team_user_id])
    assert p["pipeline"]["name"] == "my-pipeline"

    p = runner.invoke(
        ["pipeline-show", p["pipeline"]["id"]]
    )
    assert p["pipeline"]["name"] == "my-pipeline"


def test_list_pipeline(runner, team_user_id):
    for i in range(3):
        p = runner.invoke(
            ["pipeline-create", "--name", "my-pipeline-%s" % i, "--team-id",
             team_user_id])
        assert p["pipeline"]["name"] == "my-pipeline-%s" % i
    ps = runner.invoke(["pipeline-list"])
    assert len(ps["pipelines"]) == 3


def test_list_jobs_pipeline(runner, team_user_id, product_id, dci_context_remoteci):
    p = runner.invoke(
        ["pipeline-create", "--name", "my-pipeline", "--team-id", team_user_id])
    assert p["pipeline"]["name"] == "my-pipeline"

    topic = runner.invoke(
        [
            "topic-create",
            "--name",
            "osp",
            "--component_types",
            "type_1",
            "--no-export-control",
            "--product-id",
            product_id,
        ]
    )["topic"]

    runner.invoke(["topic-attach-team", topic["id"], "--team-id", team_user_id])

    runner.invoke(
        [
            "component-create",
            "--name",
            "foo",
            "--type",
            "type_1",
            "--topic-id",
            topic["id"],
        ]
    )["component"]

    jobs = runner.invoke(["pipeline-show-jobs", p["pipeline"]["id"]])
    assert len(jobs["jobs"]) == 0

    job.schedule(dci_context_remoteci, topic["id"], pipeline_id=p["pipeline"]["id"])

    jobs = runner.invoke(["pipeline-show-jobs", p["pipeline"]["id"]])
    assert len(jobs["jobs"]) == 1


def test_update_pipeline(runner, team_user_id):
    p = runner.invoke(
        ["pipeline-create", "--name", "my-pipeline", "--team-id", team_user_id])
    runner.invoke(
        ["pipeline-update",
         p["pipeline"]["id"],
         "--etag", p["pipeline"]["etag"],
         "--name", "new-pipeline"])
    p = runner.invoke(
        ["pipeline-show", p["pipeline"]["id"]]
    )

    assert p["pipeline"]["name"] == "new-pipeline"


def test_delete_pipeline(runner, team_user_id):
    p = runner.invoke(
        ["pipeline-create", "--name", "my-pipeline", "--team-id", team_user_id])
    assert p["pipeline"]["name"] == "my-pipeline"
    dp = runner.invoke_raw(
        ["pipeline-delete", p["pipeline"]["id"], "--etag", p["pipeline"]["etag"]]
    )
    assert dp.status_code == 204
    ps = runner.invoke(["pipeline-list"])
    assert len(ps["pipelines"]) == 0
