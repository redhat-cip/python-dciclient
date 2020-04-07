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

from mock import patch
import pytest
from pytest import raises
from six.moves import StringIO
from dciclient.v1.shell_commands.cli import parse_arguments, _default_dci_cs_url
from dciclient.version import __version__


@patch("sys.exit")
@patch("sys.stderr", new_callable=StringIO)
def test_parse_arguments_version(sys_stderr, exit_function):
    parse_arguments(["--version", "user-list"])
    sys_stderr.seek(0)
    assert sys_stderr.read() == "dcictl {}\n".format(__version__)
    assert exit_function.called


def test_parse_arguments_format():
    args = parse_arguments(["--format", "json", "user-list"])
    assert args.format == "json"
    args = parse_arguments(["--format", "csv", "user-list"])
    assert args.format == "csv"
    args = parse_arguments(["--format", "tsv", "user-list"])
    assert args.format == "tsv"
    args = parse_arguments(["user-list"])
    assert args.format == "table"


def test_parse_arguments_dci_login():
    args = parse_arguments(["--dci-login", "foo", "user-list"], {"DCI_LOGIN": "foo"})
    assert args.dci_login == "foo"


def test_parse_arguments_dci_login_from_env():
    args = parse_arguments(["user-list"], {"DCI_LOGIN": "foo"})
    assert args.dci_login == "foo"


def test_parse_arguments_dci_login_overload_from_env():
    args = parse_arguments(["--dci-login", "bar", "user-list"], {"DCI_LOGIN": "foo"})
    assert args.dci_login == "bar"


def test_parse_arguments_dci_password():
    args = parse_arguments(["--dci-password", "foo", "user-list"])
    assert args.dci_password == "foo"


def test_parse_arguments_dci_password_from_env():
    args = parse_arguments(["user-list"], {"DCI_PASSWORD": "foo"})
    assert args.dci_password == "foo"


def test_parse_arguments_dci_password_overload_from_env():
    args = parse_arguments(
        ["--dci-password", "bar", "user-list"], {"DCI_PASSWORD": "foo"}
    )
    assert args.dci_password == "bar"


def test_parse_arguments_dci_client_id():
    args = parse_arguments(["--dci-client-id", "foo", "user-list"])
    assert args.dci_client_id == "foo"


def test_parse_arguments_dci_client_id_from_env():
    args = parse_arguments(["user-list"], {"DCI_CLIENT_ID": "foo"})
    assert args.dci_client_id == "foo"


def test_parse_arguments_dci_client_id_overload_from_env():
    args = parse_arguments(
        ["--dci-client-id", "bar", "user-list"], {"DCI_CLIENT_ID": "foo"}
    )
    assert args.dci_client_id == "bar"


def test_parse_arguments_dci_api_secret():
    args = parse_arguments(["--dci-api-secret", "foo", "user-list"])
    assert args.dci_api_secret == "foo"


def test_parse_arguments_dci_api_secret_from_env():
    args = parse_arguments(["user-list"], {"DCI_API_SECRET": "foo"})
    assert args.dci_api_secret == "foo"


def test_parse_arguments_dci_api_secret_overload_from_env():
    args = parse_arguments(
        ["--dci-api-secret", "bar", "user-list"], {"DCI_API_SECRET": "foo"}
    )
    assert args.dci_api_secret == "bar"


def test_parse_arguments_dci_cs_url_default():
    args = parse_arguments(["user-list"])
    assert args.dci_cs_url == _default_dci_cs_url


def test_parse_arguments_dci_cs_url():
    args = parse_arguments(["--dci-cs-url", "foo", "user-list"])
    assert args.dci_cs_url == "foo"


def test_parse_arguments_dci_cs_url_from_env():
    args = parse_arguments(["user-list"], {"DCI_CS_URL": "foo"})
    assert args.dci_cs_url == "foo"


def test_parse_arguments_dci_cs_url_overload_from_env():
    args = parse_arguments(["--dci-cs-url", "bar", "user-list"], {"DCI_CS_URL": "foo"})
    assert args.dci_cs_url == "bar"


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


# fear test
@patch("sys.exit")
def test_parse_arguments_user_create_mutually_exclusive_boolean_flags(exit_function):
    with raises(TypeError):
        parse_arguments(
            [
                "user-create",
                "--name",
                "foo",
                "--password",
                "bar",
                "--email",
                "foo@foo.bar",
                "--active",
                "--no-active",
            ]
        )
        assert exit_function.called


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
