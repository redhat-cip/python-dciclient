# -*- encoding: utf-8 -*-
#
# Copyright 2020 Red Hat, Inc.
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

import mock


def test_show(runner, jobstate_id):
    jobstate = runner.invoke(["jobstate-show", jobstate_id])["jobstate"]
    assert jobstate["id"] == jobstate_id


@mock.patch("dci.api.v1.notifications.dispatcher")
def disable_create(mock_dispatcher, runner, job_id):
    job = runner.invoke(
        [
            "jobstate-create",
            "--job-id",
            job_id,
            "--status",
            "error",
        ]
    )["jobstate"]
    assert job["status"] == "error"


@mock.patch("dci.api.v1.notifications.dispatcher")
def disable_create_with_comment(mock_dispatcher, runner, job_id):
    job = runner.invoke(
        [
            "jobstate-create",
            "--job-id",
            job_id,
            "--status",
            "killed",
            "--comment",
            "no empty comment",
        ]
    )["jobstate"]
    assert job["status"] == "killed"
    assert job["comment"] == "no empty comment"
