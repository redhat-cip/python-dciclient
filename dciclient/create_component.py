# -*- encoding: utf-8 -*-
#
# Copyright 2022-2023 Red Hat, Inc.
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

import os
import sys
import copy

from argparse import ArgumentParser

from dciclient.v1.api import component
from dciclient.v1.utils import active_string, validate_json
from dciclient.v1.shell_commands.cli import _create_array_argument
from dciclient.v1.shell_commands.cli import _date_isoformat
from dciclient.v1.shell_commands import context as dci_context
from dciclient.v1.shell_commands import topic
from dciclient.v1.shell_commands import team
from dciclient.v1.shell_commands import columns
from dciclient.printer import print_response


def parse_arguments(args, environment={}):
    p = ArgumentParser(
        prog="dci-create-component",
        description=(
            "Tool to create a component for DCI " "(https://docs.distributed-ci.io/)"
        ),
    )
    dci_context.parse_auth_arguments(p, environment)
    _create_array_argument(p, "--tags", help="Comma separated list of tags")
    p.add_argument(
        "--released-at",
        help="The release date",
        default=None,
        type=_date_isoformat,
    )
    p.add_argument(
        "--url",
        help="URL to look for the component",
    )
    p.add_argument(
        "--data",
        default="{}",
        help="Data to pass (JSON)",
    )
    p.add_argument(
        "--team",
        default=None,
        help="Team to use when there are multiple",
    )
    p.add_argument(
        "topic",
        help="Topic type and version, examples: OCP-4.12 or RHEL-9.1",
    )
    p.add_argument(
        "name",
        help='Name of the component, example: "my awesome component"',
        metavar="component_name",
    )
    p.add_argument(
        "version",
        help="Version of the component, example: v2.3.4",
        metavar="component_version",
    )
    p.add_argument(
        "release_tag",
        help="Release type of the component",
        type=str,
        choices=["dev", "candidate", "ga"],
    )
    args = p.parse_args(args)

    return args


def get_team_id(context, args):
    a = copy.deepcopy(args)

    # Set defaults
    a.sort = "-created_at"
    a.limit = 1
    a.offset = 0
    a.where = None if a.team is None else "name:" + a.team

    response = team.list(context, a)
    try:
        result_json = response.json()
    except Exception:
        print(response)

    if not result_json["_meta"]["count"]:
        print("Error, no team was found")
        sys.exit(1)

    return result_json["teams"][0].get("id")


def get_topic_id(context, args):
    a = copy.deepcopy(args)

    # Set defaults
    a.where = "name:%s" % args.topic
    a.sort = "-created_at"
    a.limit = 50
    a.offset = 0

    response = topic.list(context, a)
    try:
        result_json = response.json()
    except Exception:
        print(response)

    if not result_json["_meta"]["count"]:
        print("Error, no topic '%s' was found" % args.topic)
        sys.exit(1)

    return result_json["topics"][0].get("id")


def run(context, args):
    args.team_id = get_team_id(context, args)
    args.topic_id = get_topic_id(context, args)

    # Required arguments for component creation
    args.state = True
    names = args.name.split(" ")
    args.type = "-".join([name.lower() for name in names])
    args.tags += ["build:" + args.release_tag]
    capitalized_name = " ".join([name.capitalize() for name in names])
    args.display_name = "%s %s" % (capitalized_name, args.version)
    args.command = "component-create"

    params = {
        k: getattr(args, k)
        for k in [
            "display_name",
            "version",
            "type",
            "team_id",
            "topic_id",
            "state",
            "released_at",
        ]
    }
    data = validate_json(context, "data", args.data)
    params["defaults"] = {"data": data, "url": args.url, "tags": args.tags}
    params["state"] = active_string(params["state"])
    c, _ = component.get_or_create(context, **params)

    return c


def main():
    args = parse_arguments(sys.argv[1:], os.environ)

    context = dci_context.build_context(args)

    if not context:
        print("No DCI credentials provided.")
        sys.exit(1)

    response = run(context, args)
    _columns = columns.get_columns(args)
    print_response(response, args.format, args.verbose, _columns)
