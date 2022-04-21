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

import argparse
import os
import sys
from argparse import ArgumentParser
from datetime import datetime
from dciclient.version import __version__

_default_dci_cs_url = "http://127.0.0.1:5000"
_default_sso_url = "http://127.0.0.1:8180"


def _create_boolean_flags(parser, flags, default, dest=None):
    flags = flags.split("/")
    dest = dest if dest else flags[0].strip("--")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(flags[0], action="store_true", default=default, dest=dest)
    group.add_argument(flags[1], action="store_false", dest=dest)


def _create_array_argument(parser, argument_name, help):
    parser.add_argument(
        argument_name,
        type=lambda x: [v.strip() for v in x.split(",")],
        help=help,
        default=[],
    )


def _date_isoformat(v):
    try:
        datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        raise argparse.ArgumentTypeError("'%s' is not an iso format date" % v)
    return v


def parse_arguments(args, environment={}):
    base_parser = ArgumentParser(add_help=False)
    base_parser.add_argument("--verbose", "--long", default=False, action="store_true")

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
        "--sso-url",
        default=environment.get("SSO_URL", _default_sso_url),
        help="SSO url, default to '%s'." % _default_sso_url,
    )
    parser.add_argument(
        "--sso-username",
        default=environment.get("SSO_USERNAME"),
        help="SSO username or 'SSO_USERNAME' environment variable.",
    )
    parser.add_argument(
        "--sso-password",
        default=environment.get("SSO_PASSWORD"),
        help="SSO password or 'SSO_PASSWORD' environment variable.",
    )
    parser.add_argument(
        "--sso-token",
        default=environment.get("SSO_TOKEN"),
        help="SSO token or 'SSO_TOKEN' environment variable.",
    )
    parser.add_argument(
        "--refresh-sso-token",
        default=False,
        action="store_true",
        help="Refresh the token",
    )
    parser.add_argument(
        "--format",
        default=os.environ.get("DCI_FORMAT", "table"),
        choices=["table", "json", "csv", "tsv"],
        help="Output format",
    )

    subparsers = parser.add_subparsers()
    # user commands
    p = subparsers.add_parser(
        "user-list", help="List all users.", parents=[base_parser]
    )
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="user-list")

    p = subparsers.add_parser(
        "user-create", help="Create a user.", parents=[base_parser]
    )
    p.add_argument("--name", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--email", required=True)
    p.add_argument("--fullname")
    _create_boolean_flags(p, "--active/--no-active", default=True, dest="state")
    p.add_argument("--team-id")
    p.set_defaults(command="user-create")

    p = subparsers.add_parser(
        "user-update", help="Update a user.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.add_argument("--name")
    p.add_argument("--fullname", default="")
    p.add_argument("--email")
    p.add_argument("--password")
    p.add_argument("--team-id")
    _create_boolean_flags(p, "--active/--no-active", default=None, dest="state")
    p.set_defaults(command="user-update")

    p = subparsers.add_parser(
        "user-delete", help="Update a user.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.set_defaults(command="user-delete")

    p = subparsers.add_parser("user-show", help="Show a user.", parents=[base_parser])
    p.add_argument("id")
    p.set_defaults(command="user-show")

    # team commands
    p = subparsers.add_parser(
        "team-list", help="List all teams.", parents=[base_parser]
    )
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="team-list")

    p = subparsers.add_parser(
        "team-create", help="Create a team.", parents=[base_parser]
    )
    p.add_argument("--name", required=True)
    p.add_argument("--country")
    _create_boolean_flags(p, "--active/--no-active", default=True, dest="state")
    p.set_defaults(command="team-create")

    p = subparsers.add_parser(
        "team-update", help="Update a team.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.add_argument("--name")
    p.add_argument("--country")
    _create_boolean_flags(p, "--active/--no-active", default=None, dest="state")
    _create_boolean_flags(p, "--external/--no-external", default=None, dest="external")
    p.set_defaults(command="team-update")

    p = subparsers.add_parser(
        "team-delete", help="Update a team.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.set_defaults(command="team-delete")

    p = subparsers.add_parser("team-show", help="Show a team.", parents=[base_parser])
    p.add_argument("id")
    p.set_defaults(command="team-show")

    # product commands
    p = subparsers.add_parser(
        "product-list", help="List all products.", parents=[base_parser]
    )
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="product-list")

    p = subparsers.add_parser(
        "product-create", help="Create a product.", parents=[base_parser]
    )
    p.add_argument("--name", required=True)
    p.add_argument("--label")
    p.add_argument("--description")
    _create_boolean_flags(p, "--active/--no-active", default=True, dest="state")
    p.set_defaults(command="product-create")

    p = subparsers.add_parser(
        "product-update", help="Update a product.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.add_argument("--name")
    p.add_argument("--label")
    p.add_argument("--description")
    _create_boolean_flags(p, "--active/--no-active", default=None, dest="state")
    _create_boolean_flags(p, "--external/--no-external", default=None, dest="external")
    p.set_defaults(command="product-update")

    p = subparsers.add_parser(
        "product-delete", help="Update a product.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.set_defaults(command="product-delete")

    p = subparsers.add_parser(
        "product-show", help="Show a product.", parents=[base_parser]
    )
    p.add_argument("id")
    p.set_defaults(command="product-show")

    p = subparsers.add_parser(
        "product-attach-team", help="Attach team to a product.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--team-id")
    p.set_defaults(command="product-attach-team")

    p = subparsers.add_parser(
        "product-detach-team", help="Detach team to a product.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--team-id")
    p.set_defaults(command="product-detach-team")

    p = subparsers.add_parser(
        "product-list-teams",
        help="List all teams attached to a product.",
        parents=[base_parser],
    )
    p.add_argument("id")
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="product-list-teams")

    # feeder commands
    p = subparsers.add_parser(
        "feeder-list", help="List all feeders.", parents=[base_parser]
    )
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="feeder-list")

    p = subparsers.add_parser(
        "feeder-create", help="Create a feeder.", parents=[base_parser]
    )
    p.add_argument("--name", required=True)
    p.add_argument("--data")
    _create_boolean_flags(p, "--active/--no-active", default=True, dest="state")
    p.add_argument("--team-id")
    p.set_defaults(command="feeder-create")

    p = subparsers.add_parser(
        "feeder-update", help="Update a feeder.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.add_argument("--name")
    p.add_argument("--data")
    p.add_argument("--team-id")
    _create_boolean_flags(p, "--active/--no-active", default=None, dest="state")
    p.set_defaults(command="feeder-update")

    p = subparsers.add_parser(
        "feeder-delete", help="Update a feeder.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.set_defaults(command="feeder-delete")

    p = subparsers.add_parser(
        "feeder-show", help="Show a feeder.", parents=[base_parser]
    )
    p.add_argument("id")
    p.set_defaults(command="feeder-show")

    p = subparsers.add_parser(
        "feeder-reset-api-secret",
        help="reset api secret for a feeder.",
        parents=[base_parser],
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.set_defaults(command="feeder-reset-api-secret")

    # topic commands
    p = subparsers.add_parser(
        "topic-list", help="List all topics.", parents=[base_parser]
    )
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="topic-list")

    p = subparsers.add_parser(
        "topic-create", help="Create a topic.", parents=[base_parser]
    )
    p.add_argument("--name", required=True)
    p.add_argument("--product-id")
    p.add_argument(
        "--component_types", default=None, help="Component types separated by commas."
    )
    _create_boolean_flags(p, "--active/--no-active", default=True, dest="state")
    _create_boolean_flags(
        p, "--export-control/--no-export-control", default=False, dest="export_control"
    )
    p.add_argument("--data")
    p.set_defaults(command="topic-create")

    p = subparsers.add_parser(
        "topic-update", help="Update a topic.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.add_argument("--name")
    p.add_argument(
        "--component_types", default=None, help="Component types separated by commas."
    )
    p.add_argument("--next-topic-id")
    _create_boolean_flags(p, "--active/--no-active", default=False, dest="state")
    _create_boolean_flags(
        p, "--export-control/--no-export-control", default=None, dest="export_control"
    )
    p.add_argument("--product-id")
    p.add_argument("--data")
    p.set_defaults(command="topic-update")

    p = subparsers.add_parser(
        "topic-delete", help="Delete a topic.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.set_defaults(command="topic-delete")

    p = subparsers.add_parser("topic-show", help="Show a topic.", parents=[base_parser])
    p.add_argument("id")
    p.set_defaults(command="topic-show")

    p = subparsers.add_parser(
        "topic-attach-team", help="Attach a team to a topic.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--team-id")
    p.set_defaults(command="topic-attach-team")

    p = subparsers.add_parser(
        "topic-unattach-team", help="Unattach a team to a topic.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--team-id")
    p.set_defaults(command="topic-unattach-team")

    p = subparsers.add_parser(
        "topic-list-team", help="List teams attached to a topic.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="topic-list-team")

    # jobstate commands
    p = subparsers.add_parser(
        "jobstate-show", help="Show a jobstate.", parents=[base_parser]
    )
    p.add_argument("id")
    p.set_defaults(command="jobstate-show")

    p = subparsers.add_parser(
        "jobstate-create", help="Create a jobstate.", parents=[base_parser]
    )
    p.add_argument("--job-id", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--comment", default='')
    p.set_defaults(command="jobstate-create")

    # component commands
    p = subparsers.add_parser(
        "component-list", help="List all components.", parents=[base_parser]
    )
    p.add_argument("--topic-id", required=True, dest="id")
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="component-list")

    p = subparsers.add_parser(
        "component-create", help="Create a component.", parents=[base_parser]
    )
    p.add_argument("--name", required=True, help="Name of component")
    p.add_argument("--type", required=True, help="Type of component")
    p.add_argument("--topic-id", required=True, help="Topic ID")
    p.add_argument("--team-id")
    _create_array_argument(p, "--tags", help="Comma separated list of tags")
    p.add_argument(
        "--canonical_project_name", default=None, help="Canonical project name."
    )
    p.add_argument("--title", help="Title of component")
    p.add_argument("--message", help="Component message")
    p.add_argument("--url", help="URL to look for the component")
    _create_boolean_flags(p, "--active/--no-active", default=True, dest="state")
    p.add_argument("--data", default="{}", help="Data to pass (JSON)")
    p.add_argument(
        "--released-at", default=None, type=_date_isoformat, help="The release date"
    )
    p.set_defaults(command="component-create")

    p = subparsers.add_parser(
        "component-update", help="Update a component.", parents=[base_parser]
    )
    p.add_argument("id")
    _create_boolean_flags(p, "--active/--no-active", default=None, dest="state")
    p.add_argument("--name", required=False, help="Name of component")
    p.add_argument("--type", required=False, help="Type of component")
    _create_array_argument(p, "--tags", help="Comma separated list of tags")
    p.add_argument(
        "--canonical_project_name", default=None, help="Canonical project name."
    )
    p.add_argument("--title", help="Title of component")
    p.add_argument("--message", help="Component message")
    p.add_argument("--url", help="URL to look for the component")
    p.add_argument("--data", default="{}", help="Data to pass (JSON)")
    p.set_defaults(command="component-update")

    p = subparsers.add_parser(
        "component-delete", help="Delete a component.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.set_defaults(command="component-delete")

    p = subparsers.add_parser(
        "component-show", help="Show a component.", parents=[base_parser]
    )
    p.add_argument("id")
    p.set_defaults(command="component-show")

    p = subparsers.add_parser(
        "component-file-upload",
        help="Attach a file to a component.",
        parents=[base_parser],
    )
    p.add_argument("id")
    p.add_argument("--path", required=True)
    p.set_defaults(command="component-file-upload")

    p = subparsers.add_parser(
        "component-file-show", help="Show a component file.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--file-id", required=True)
    p.set_defaults(command="component-file-show")

    p = subparsers.add_parser(
        "component-file-download",
        help="Retrieve a component file.",
        parents=[base_parser],
    )
    p.add_argument("id")
    p.add_argument("--file-id", required=True)
    p.add_argument("--target", required=True)
    p.set_defaults(command="component-file-download")

    p = subparsers.add_parser(
        "component-file-list",
        help="List files attached to a component.",
        parents=[base_parser],
    )
    p.add_argument("id")
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="component-file-list")

    p = subparsers.add_parser(
        "component-file-delete", help="Delete a component file.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--file-id", required=True)
    p.add_argument("--etag", required=True)
    p.set_defaults(command="component-file-delete")

    # file commands
    p = subparsers.add_parser(
        "file-list", help="List all files.", parents=[base_parser]
    )
    p.add_argument("job_id")
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="file-list")

    p = subparsers.add_parser("file-show", help="Show a file.", parents=[base_parser])
    p.add_argument("id")
    p.set_defaults(command="file-show")

    p = subparsers.add_parser(
        "file-delete", help="Delete a file.", parents=[base_parser]
    )
    p.add_argument("id")
    p.set_defaults(command="file-delete")

    # job commands
    p = subparsers.add_parser("job-list", help="List all jobs.", parents=[base_parser])
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=10)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="job-list")

    p = subparsers.add_parser("job-show", help="Show a job.", parents=[base_parser])
    p.add_argument("id")
    p.set_defaults(command="job-show")

    p = subparsers.add_parser("job-delete", help="Delete a job.", parents=[base_parser])
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.set_defaults(command="job-delete")

    p = subparsers.add_parser(
        "job-results", help="List all job results.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.set_defaults(command="job-results")

    p = subparsers.add_parser(
        "job-output", help="Show the job output.", parents=[base_parser]
    )
    p.add_argument("id")
    p.set_defaults(command="job-output")

    p = subparsers.add_parser(
        "job-upload-file", help="Attach a file to a job.", parents=[base_parser]
    )
    p.add_argument("job_id")
    p.add_argument("--name", required=True)
    p.add_argument("--path", required=True, dest="file_path")
    p.add_argument("--jobstate-id")
    p.add_argument("--mime")
    p.set_defaults(command="job-upload-file")

    p = subparsers.add_parser(
        "job-download-file", help="Retrieve a job file.", parents=[base_parser]
    )
    p.add_argument("id", help="The job id.")
    p.add_argument("--file-id", required=True)
    p.add_argument("--target", required=True, help="Destination file path.")
    p.set_defaults(command="job-download-file")

    p = subparsers.add_parser(
        "job-show-file", help="Show a job file.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--file-id", required=True)
    p.set_defaults(command="job-show-file")

    p = subparsers.add_parser(
        "job-list-file", help="List files attached to a job.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="job-list-file")

    p = subparsers.add_parser(
        "job-delete-file", help="Delete a job file.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--file-id", required=True)
    p.set_defaults(command="job-delete-file")

    # remoteci commands
    p = subparsers.add_parser(
        "remoteci-list", help="List all remotecis.", parents=[base_parser]
    )
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="remoteci-list")

    p = subparsers.add_parser(
        "remoteci-create", help="Create a remoteci.", parents=[base_parser]
    )
    p.add_argument("--name", required=True)
    p.add_argument("--team-id", required=False)
    p.add_argument("--data", default="{}")
    _create_boolean_flags(p, "--active/--no-active", default=None, dest="state")
    p.set_defaults(command="remoteci-create")

    p = subparsers.add_parser(
        "remoteci-update", help="Update a remoteci.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.add_argument("--name")
    p.add_argument("--team-id")
    p.add_argument("--data", default="{}")
    _create_boolean_flags(p, "--active/--no-active", default=None, dest="state")
    p.set_defaults(command="remoteci-update")

    p = subparsers.add_parser(
        "remoteci-delete", help="Delete a remoteci.", parents=[base_parser]
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.set_defaults(command="remoteci-delete")

    p = subparsers.add_parser(
        "remoteci-show", help="Show a remoteci.", parents=[base_parser]
    )
    p.add_argument("id")
    p.set_defaults(command="remoteci-show")

    p = subparsers.add_parser(
        "remoteci-get-data",
        help="Retrieve data field from a remoteci.",
        parents=[base_parser],
    )
    p.add_argument("id")
    p.add_argument("--keys", default=None)
    p.set_defaults(command="remoteci-get-data")

    p = subparsers.add_parser(
        "remoteci-reset-api-secret",
        help="Reset a remoteci api secret.",
        parents=[base_parser],
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.set_defaults(command="remoteci-reset-api-secret")

    p = subparsers.add_parser(
        "remoteci-refresh-keys",
        help="Refresh a remoteci key pair.",
        parents=[base_parser],
    )
    p.add_argument("id")
    p.add_argument("--etag", required=True)
    p.set_defaults(command="remoteci-refresh-keys")

    p = subparsers.add_parser(
        "remoteci-attach-user",
        help="Attach a user to a remoteci.",
        parents=[base_parser],
    )
    p.add_argument("id")
    p.add_argument("--user-id", required=True)
    p.set_defaults(command="remoteci-attach-user")

    p = subparsers.add_parser(
        "remoteci-unattach-user",
        help="Unattach a user to a remoteci.",
        parents=[base_parser],
    )
    p.add_argument("id")
    p.add_argument("--user-id", required=True)
    p.set_defaults(command="remoteci-unattach-user")

    p = subparsers.add_parser(
        "remoteci-list-user",
        help="List users attached to a remoteci.",
        parents=[base_parser],
    )
    p.add_argument("id")
    p.add_argument("--sort", default="-created_at")
    p.add_argument("--limit", default=50)
    p.add_argument("--offset", default=0)
    p.add_argument("--where", help="Optional filter criteria", required=False)
    p.set_defaults(command="remoteci-list-user")

    # purge commands
    p = subparsers.add_parser(
        "purge", help="Purge soft-deleted resources.", parents=[base_parser]
    )
    p.add_argument(
        "--resource", default=None, help="Comma separated list of resource to purge."
    )
    p.add_argument(
        "--force", default=False, action="store_true", help="Purge resources."
    )
    p.set_defaults(command="purge")

    args = parser.parse_args(args)

    if "command" not in args:
        parser.print_help()
        sys.exit()

    return args
