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

import sys
from mock import patch
from pytest import raises
from dciclient.v1.shell_commands.cli import parse_arguments, _default_dci_cs_url
from dciclient.version import __version__


@patch("sys.exit")
def test_parse_arguments_version(exit_function, capsys):
    parse_arguments(["--version", "user-list"])
    captured = capsys.readouterr()
    # Note(hguemar): argparse behaviour here changed on py3k
    if sys.version_info > (3, 0):
        captured = captured.out
    else:
        captured = captured.err
    assert captured == "dcictl {}\n".format(__version__)
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


def test_parse_arguments_sso():
    args = parse_arguments(
        [
            "--sso-url",
            "https://sso.redhat.com",
            "--sso-username",
            "dci",
            "--sso-password",
            "dci",
            "user-list",
        ],
        {},
    )

    assert args.sso_url == "https://sso.redhat.com"
    assert args.sso_username == "dci"
    assert args.sso_password == "dci"
    assert args.sso_token is None
    assert args.refresh_sso_token is False


def test_parse_arguments_sso_env():
    args = parse_arguments(
        ["user-list"],
        {
            "SSO_URL": "https://sso.redhat.com",
            "SSO_USERNAME": "sso",
            "SSO_PASSWORD": "sso",
        },
    )

    assert args.sso_url == "https://sso.redhat.com"
    assert args.sso_username == "sso"
    assert args.sso_password == "sso"
    assert args.sso_token is None
    assert args.refresh_sso_token is False


def test_parse_arguments_sso_token():
    args = parse_arguments(
        ["--sso-token", "abc", "--refresh-sso-token", "user-list"], {}
    )

    assert args.refresh_sso_token
    assert args.sso_token == "abc"


def test_parse_arguments_sso_token_env():
    args = parse_arguments(["user-list"], {"SSO_TOKEN": "efg"})

    assert args.sso_token == "efg"
    assert args.refresh_sso_token is False


def test_verbose():
    args = parse_arguments(
        [
            "user-create",
            "--name",
            "toto",
            "--password",
            "toto",
            "--email",
            "toto@example.org",
        ]
    )
    assert args.verbose is False

    args = parse_arguments(
        [
            "user-create",
            "--verbose",
            "--name",
            "toto",
            "--password",
            "toto",
            "--email",
            "toto@example.org",
        ]
    )
    assert args.verbose is True

    args = parse_arguments(
        [
            "user-create",
            "--long",
            "--name",
            "toto",
            "--password",
            "toto",
            "--email",
            "toto@example.org",
        ]
    )
    assert args.verbose is True
