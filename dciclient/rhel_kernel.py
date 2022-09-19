#
# Copyright (C) Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import sys
from argparse import ArgumentParser

from dciclient.v1.api import topic
from dciclient.v1.api import product
from dciclient.v1.shell_commands import context as dci_context


_DEFAULT_DCI_CS_URL = "http:://127.0.0.1:5000"


def parse_arguments(args, environment={}):
    parser = ArgumentParser()
    dci_context.parse_arguments(parser, args, environment)
    parser.add_argument(
        "--topic",
        dest="topic_name",
        help="topic name",
    )

    parser.add_argument(
        "--topic-list",
        default=False,
        action="store_true",
        help="list the available topics",
    )

    return parser.parse_args(args)


def get_available_topics(context):
    product_list = product.list(context=context, where="name:RHEL").json()
    rhel_id = product_list["products"][0]["id"]
    topic_list = topic.list(
        context=context, where="product_id:%s,state:active" % rhel_id, sort="-name"
    ).json()
    return [t["name"] for t in topic_list["topics"]]


def print_available_topics(context):
    available_topics = get_available_topics(context)
    print("available topics:")
    print("\n".join(available_topics))


def get_topic_id_from_name(context, name):
    topic_list = topic.list(context=context, where="name:%s,state:active" % name).json()
    if not topic_list["topics"]:
        print("topic %s not found\n" % name)
        print_available_topics(context)
        sys.exit(1)
    return topic_list["topics"][0]["id"]


def main():
    args = parse_arguments(sys.argv[1:], os.environ)

    context = dci_context.build_context(args)

    if not context:
        print("No DCI credentials provided.")
        sys.exit(1)

    if args.topic_list:
        print_available_topics(context)
        sys.exit(0)

    topic_id = get_topic_id_from_name(context, args.topic_name)
    latest_component = topic.list_components(
        context,
        topic_id,
        sort="-created_at",
        limit=1,
        offset=0,
        where="type:compose,state:active",
    ).json()

    if not latest_component["components"]:
        print("no components found")
        sys.exit(1)
    latest_component = latest_component["components"][0]
    kernel_found = False
    for tag in latest_component["tags"]:
        if tag.startswith("kernel:"):
            kernel_found = True
            print(tag.split(":")[1])
            break

    if not kernel_found:
        print(
            "no kernel information found in the component %s" % latest_component["id"]
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
