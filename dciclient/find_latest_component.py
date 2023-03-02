# -*- encoding: utf-8 -*-
#
# Copyright 2022 Red Hat, Inc.
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
from dciclient.v1.shell_commands.cli import _create_array_argument
from dciclient.v1.shell_commands import context as dci_context
from dciclient.v1.shell_commands import component
from dciclient.v1.shell_commands import topic
from dciclient.v1.shell_commands import product
from dciclient.printer import print_result


COLUMNS = [
    "display_name",
    "created_at",
    "data",
    "etag",
    "id",
    "released_at",
    "state",
    "tags",
    "team_id",
    "topic_id",
    "type",
    "updated_at",
    "url",
    "version"
]


def parse_arguments(args, environment={}):
    p = ArgumentParser(
        prog="dci-find-latest-component",
        description=(
            "Tool to find the latest component in DCI "
            "(https://docs.distributed-ci.io/)"
        ),
    )
    dci_context.parse_auth_arguments(p, environment)
    _create_array_argument(p, "--tags", help="Comma separated list of tags")
    p.add_argument(
        "--topic",
        help="Topic type and version, examples: OCP-4.12 or RHEL-9.1",
    )
    p.add_argument(
        "product",
        help=("Product to look for the component. "
              "For example, OpenShift, OpenStack or RHEL."),
    )
    p.add_argument(
        "type",
        help='Name of the component, example: my-awesome-component',
        metavar="component_name",
    )
    args = p.parse_args(args)
    args.command = "component-list"

    return args


def get_product_id(context, args):
    a = copy.deepcopy(args)

    # Set defaults
    a.sort = "-created_at"
    a.limit = 1
    a.offset = 0
    a.where = "name:" + a.product

    response = product.list(context, a)
    try:
        result_json = response.json()
    except Exception:
        print(response)

    if response.status_code // 100 != 2 or not result_json["_meta"]["count"]:
        sys.stderr.write("Error, product '%s' was not found\n" % a.product)
        return None

    return result_json["products"][0].get("id")


def get_topic_id(context, args):
    a = copy.deepcopy(args)

    # Set defaults
    a.where = "name:%s" % args.topic
    a.sort = "-created_at"
    a.limit = 1
    a.offset = 0

    response = topic.list(context, a)
    try:
        result_json = response.json()
    except Exception:
        sys.stderr.write(response)
        return None

    if response.status_code // 100 != 2 or not result_json["_meta"]["count"]:
        sys.stderr.write("Error, topic '%s' was not found\n" % args.topic)
        return None

    return result_json["topics"][0].get("id")


def get_topic_ids(context, args):
    a = copy.deepcopy(args)

    # Set defaults
    a.where = None
    a.sort = "-created_at"
    a.limit = 50
    a.offset = 0

    response = topic.list(context, a)
    try:
        result_json = response.json()
    except Exception:
        sys.stderr.write(response)
        return []

    if not result_json["_meta"]["count"]:
        sys.stderr.write("Error, no topic was found for product %s (%s)\n"
                         % (args.product, args.product_id))
        return []

    return [res.get("id") for res in result_json["topics"]]


def lookup_latest_component(context, args):
    a = copy.deepcopy(args)

    # Set defaults
    a.where = "type:" + a.type + ((",tags:" + ",tags:".join(a.tags))
                                  if len(a.tags) != 0 else "")
    a.sort = "-released_at"
    a.limit = 1
    a.offset = 0
    a.id = a.topic_id

    response = component.list(context, a)
    try:
        result_json = response.json()
    except Exception:
        sys.stderr.write(response)
        return None
    if response.status_code // 100 != 2 or not result_json["_meta"]["count"]:
        return None

    return result_json["components"][0]


def run(context, args):
    args.product_id = get_product_id(context, args)

    if args.topic:
        args.topic_id = get_topic_id(context, args)
        return lookup_latest_component(context, args)
    else:
        for topic_id in get_topic_ids(context, args):
            args.topic_id = topic_id
            comp = lookup_latest_component(context, args)
            if comp:
                return comp
    return None


def main():
    args = parse_arguments(sys.argv[1:], os.environ)

    context = dci_context.build_context(args)

    if not context:
        sys.stderr.write("No DCI credentials provided\n.")
        return 1

    result = run(context, args)
    if result:
        print_result(result, args.format, args.verbose, COLUMNS)
        return 0
    else:
        sys.stderr.write("No component found for %s on the %s product\n"
                         % (args.type, args.product))
        return 1
