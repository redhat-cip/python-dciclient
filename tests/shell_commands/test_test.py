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

import pytest
from dciclient.v1.exceptions import BadParameter


def test_create_list(runner):
    runner.invoke(["test-create", "--name", "foo"])
    runner.invoke(["test-create", "--name", "bar"])
    tests = runner.invoke(["test-list"])["tests"]
    assert len(tests) == 2
    assert tests[0]["name"] == "bar"
    assert tests[1]["name"] == "foo"


def test_create_inactive(runner):
    test = runner.invoke(["test-create", "--name", "foo", "--no-active"])["test"]
    assert test["state"] == "inactive"


def test_create_data(runner):
    test = runner.invoke(["test-create", "--name", "foo", "--data", '{"Foo": 2}'])[
        "test"
    ]
    assert test["name"] == "foo"


def test_create_bad_data(runner):
    with pytest.raises(BadParameter):
        runner.invoke_raw(["test-create", "--name", "foo", "--data", "{Foo: 2}"])


def test_update_active(runner):
    test = runner.invoke(["test-create", "--name", "foo", "--data", '{"Foo": 2}'])[
        "test"
    ]

    assert test["state"] == "active"

    result = runner.invoke(
        ["test-update", test["id"], "--etag", test["etag"], "--no-active"]
    )

    assert result["test"]["id"] == test["id"]
    assert result["test"]["state"] == "inactive"

    result = runner.invoke(
        [
            "test-update",
            test["id"],
            "--etag",
            result["test"]["etag"],
            "--name",
            "foobar",
        ]
    )

    assert result["test"]["id"] == test["id"]
    assert result["test"]["state"] == "inactive"
    assert result["test"]["name"] == "foobar"

    result = runner.invoke(
        ["test-update", test["id"], "--etag", result["test"]["etag"], "--active"]
    )

    assert result["test"]["state"] == "active"


def test_delete(runner):
    test = runner.invoke(["test-create", "--name", "foo"])["test"]
    tests = runner.invoke(["test-list"])["tests"]
    len_tests = len(tests)

    runner.invoke_raw(["test-delete", test["id"]])
    tests = runner.invoke(["test-list"])["tests"]
    len_tests2 = len(tests)

    assert len_tests2 == (len_tests - 1)


def test_show(runner):
    test = runner.invoke(["test-create", "--name", "foo"])["test"]

    test = runner.invoke(["test-show", test["id"]])["test"]

    assert test["name"] == "foo"
