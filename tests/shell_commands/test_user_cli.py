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

import pytest

from mock import patch
from dciclient.v1.shell_commands.cli import parse_arguments


def test_parse_arguments_user_list_defaults():
    args = parse_arguments(["user-list"])
    assert args.command == "user-list"
    assert args.sort == "-created_at"
    assert args.limit == 50
    assert args.offset == 0
    assert args.where is None
    assert args.verbose is False


@pytest.mark.parametrize(
    "params",
    [
        ["user-create"],
        ["user-create", "--name", "foo"],
        ["user-create", "--name", "foo", "--password", "bar"],
    ],
)
@patch("sys.exit")
def test_parse_arguments_user_create_no_required_args_exit(exit_function, params):
    parse_arguments(params)
    assert exit_function.called


@patch("sys.exit")
def test_parse_arguments_user_create_required_args_no_exit(exit_function):
    args = parse_arguments(
        ["user-create", "--name", "foo", "--password", "bar", "--email", "foo@foo.bar"]
    )
    assert args.command == "user-create"
    assert args.name == "foo"
    assert args.password == "bar"
    assert args.email == "foo@foo.bar"
    assert not exit_function.called


def test_parse_arguments_user_create_boolean_flags():
    args = parse_arguments(
        [
            "user-create",
            "--name",
            "foo",
            "--password",
            "bar",
            "--email",
            "foo@foo.bar",
            "--active",
        ]
    )
    assert args.state
    args = parse_arguments(
        [
            "user-create",
            "--name",
            "foo",
            "--password",
            "bar",
            "--email",
            "foo@foo.bar",
            "--no-active",
        ]
    )
    assert args.state is False


def test_parse_arguments_user_create_active_default():
    args = parse_arguments(
        ["user-create", "--name", "foo", "--password", "bar", "--email", "foo@foo.bar"]
    )
    assert args.state is True


def test_parse_arguments_user_update():
    args = parse_arguments(["user-update", "u1", "--etag", "e1", "--name", "new_name"])
    assert args.command == "user-update"
    assert args.id == "u1"
    assert args.etag == "e1"
    assert args.name == "new_name"


def test_parse_arguments_user_delete():
    args = parse_arguments(["user-delete", "u1", "--etag", "e1"])
    assert args.command == "user-delete"
    assert args.id == "u1"
    assert args.etag == "e1"
