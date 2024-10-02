# -*- encoding: utf-8 -*-
#
# Copyright 2024 Red Hat, Inc.
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
import pytest


def test_download_pull_secret(tmp_path, runner, rhel10_topic):
    pull_secret = rhel10_topic["data"]["pull_secret"]
    destination_file = tmp_path / "auth.json"
    destination_file_path = str(destination_file)
    runner.invoke_raw(
        [
            "download-pull-secret",
            "--topic",
            rhel10_topic["name"],
            "--destination",
            destination_file_path,
        ]
    )
    with open(destination_file_path) as f:
        assert f.read() == json.dumps(pull_secret)


def test_download_pull_secret_without_a_pull_secret_in_topic_data(runner, topic):
    with pytest.raises(SystemExit):
        runner.invoke_raw(
            [
                "download-pull-secret",
                "--topic",
                topic,
                "--destination",
                "/tmp/auth.json",
            ]
        )


def test_download_pull_secret_without_specified_topic(runner):
    with pytest.raises(SystemExit):
        runner.invoke_raw(
            [
                "download-pull-secret",
                "--topic",
                "unknown-topic",
                "--destination",
                "/tmp/auth.json",
            ]
        )
