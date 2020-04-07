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

from argparse import ArgumentParser
from dciclient.version import __version__

_default_dci_cs_url = "http://127.0.0.1:5000"


def _create_boolean_flags(parser, flags, default):
    flags = flags.split("/")
    group = parser.add_mutually_exclusive_group()
    a = group.add_argument(flags[0], action="store_true", default=True)
    group.add_argument(flags[1], action="store_false", dest=a.dest)


def parse_arguments(args, environment={}):
    parser = ArgumentParser(prog="dcictl")
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )
    parser.add_argument(
        "--dci-login",
        default=environment.get("DCI_LOGIN", None),
        help="DCI login or 'DCI_LOGIN' environment variable.",
    )
    parser.add_argument(
        "--dci-password",
        default=environment.get("DCI_PASSWORD", None),
        help="DCI password or 'DCI_PASSWORD' environment variable.",
    )
    parser.add_argument(
        "--dci-client-id",
        default=environment.get("DCI_CLIENT_ID", None),
        help="DCI CLIENt ID or 'DCI_CLIENT_ID' environment variable.",
    )
    parser.add_argument(
        "--dci-api-secret",
        default=environment.get("DCI_API_SECRET", None),
        help="DCI API secret or 'DCI_API_SECRET' environment variable.",
    )
    parser.add_argument(
        "--dci-cs-url",
        default=environment.get("DCI_CS_URL", _default_dci_cs_url),
        help="DCI control server url, default to '%s'." % _default_dci_cs_url,
    )
    parser.add_argument(
        "--format",
        default="table",
        choices=["table", "json", "csv", "tsv"],
        help="Output format",
    )

    subparsers = parser.add_subparsers()
    # user commands
    p = subparsers.add_parser("user-list", help="List all users.")
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.add_argument("--verbose", default=False, action="store_true")
    p.set_defaults(command="user-list")

    p = subparsers.add_parser("user-create", help="Create a user.")
    p.add_argument("--name", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--email", required=True)
    p.add_argument("--fullname")
    _create_boolean_flags(p, "--active/--no-active", default=True)
    p.add_argument("--team-id")
    p.set_defaults(command="user-create")

    p = subparsers.add_parser("user-update", help="Update a user.")
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.add_argument("--name")
    p.add_argument("--fullname", default="")
    p.add_argument("--email")
    p.add_argument("--password")
    p.add_argument("--team-id")
    _create_boolean_flags(p, "--active/--no-active", default=True)
    p.set_defaults(command="user-update")

    p = subparsers.add_parser("user-delete", help="Update a user.")
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.set_defaults(command="user-delete")

    p = subparsers.add_parser("user-show", help="Show a user.")
    p.add_argument("id")
    p.set_defaults(command="user-show")

    args = parser.parse_args(args)
    return args
