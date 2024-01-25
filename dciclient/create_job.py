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

import os
import sys
import copy

from argparse import ArgumentParser

from dciclient.v1.api import job as dci_job
from dciclient.v1.shell_commands import context as dci_context
from dciclient.v1.shell_commands import topic
from dciclient.v1.shell_commands import component
from dciclient.v1.shell_commands import remoteci
from dciclient.v1.shell_commands import columns
from dciclient.printer import print_response


def parse_arguments(args, environment={}):
    p = ArgumentParser(
        prog="dci-create-job",
        description=(
            "Tool to create a job for DCI " "(https://docs.distributed-ci.io/)"
        ),
    )
    dci_context.parse_auth_arguments(p, environment)
    p.add_argument(
        "--tag",
        dest="tags",
        action="append",
        help="tag to attach to the job",
        default=[],
    )
    p.add_argument(
        "--key-value",
        dest="kv",
        action="append",
        help="key/value to attach to the job in the format key=value",
        default=[],
    )
    p.add_argument(
        "--url",
        help="URL to attach to the job",
    )
    p.add_argument(
        "--comment",
        help="comment to attach to the job",
    )
    p.add_argument(
        "--configuration",
        help="configuration to attach to the job",
    )
    p.add_argument(
        "--previous-job-id",
        help="previous job id to attach to the job",
    )
    p.add_argument(
        "--comp",
        dest="components",
        action="append",
        help="component name to attach to the job",
        default=[],
    )
    p.add_argument(
        "--data",
        help="JSON data to attach to the job",
    )
    # mandatory arguments
    p.add_argument(
        "--name",
        help="name of the job",
        required=True,
    )
    p.add_argument(
        "--topic",
        help="Topic name, examples: OCP-4.12 or RHEL-9.1",
        required=True,
    )
    p.add_argument(
        "--remoteci",
        help="remoteci name",
        required=True,
    )
    args = p.parse_args(args)

    return args


def get_object_id(context, args, name, types, func):
    a = copy.deepcopy(args)

    # Set defaults
    a.where = "name:%s" % name
    a.sort = "-created_at"
    a.limit = 50
    a.offset = 0

    response = func(context, a)
    try:
        result_json = response.json()
    except Exception:
        print(response)
        sys.exit(1)

    if not result_json["_meta"]["count"]:
        print("Error, no %s '%s' was found" % (types, name))
        sys.exit(1)

    return result_json[types][0].get("id")


def get_topic_id(context, args):
    return get_object_id(context, args, args.topic, "topics", topic.list)


def get_remoteci_id(context, args):
    return get_object_id(context, args, args.remoteci, "remotecis", remoteci.list)


def get_component_id(context, args, name):
    return get_object_id(context, args, name, "components", component.list)


def run(context, args):
    args.topic_id = get_topic_id(context, args)
    args.remoteci_id = get_remoteci_id(context, args)
    # required for component lookup
    args.id = args.topic_id
    args.components = [get_component_id(context, args, c_name)
                       for c_name in args.components]
    args.command = "job-create"

    params = {
        k: getattr(args, k)
        for k in [
            "comment",
            "components",
            "configuration",
            "data",
            "name",
            "previous_job_id",
            "remoteci_id",
            "tags",
            "url",
        ]
    }

    j = dci_job.create(context, args.topic_id, **params)

    job = j.json()

    if "job" not in job:
        if "payload" in job and "error" in job["payload"]:
            print("Error, unable to create job: %s" % job["payload"]["error"])
        else:
            print("Error, unable to create job")
        sys.exit(1)

    job = job["job"]

    # add key/value
    for kv in args.kv:
        key, value = kv.split("=")
        try:
            fvalue = float(value)
        except ValueError:
            fvalue = value
        res = dci_job.add_kv(context, job["id"], key, fvalue)
        try:
            result_json = res.json()
        except Exception:
            print(res)
            sys.exit(1)

        if "kv" not in result_json:
            if "payload" in result_json and "error" in result_json["payload"]:
                print("Error, unable to add key/value (%s/%s): %s"
                      % (key, value, result_json["payload"]["error"]))
            else:
                print("Error, unable to add key/value: %s/%s" % (key, value))
            sys.exit(1)

    # refresh job a key/value has been added
    if args.kv:
        j = dci_job.get(context, job["id"])
        try:
            result_json = j.json()
        except Exception:
            print(j)
            sys.exit(1)

        if "job" not in result_json:
            if "payload" in result_json and "error" in result_json["payload"]:
                print("Error, unable to refresh job: %s"
                      % result_json["payload"]["error"])
            else:
                print("Error, unable to refresh job")
            sys.exit(1)

        job = result_json["job"]

    return j


def main():
    args = parse_arguments(sys.argv[1:], os.environ)

    context = dci_context.build_context(args)

    if not context:
        print("No DCI credentials provided.")
        sys.exit(1)

    response = run(context, args)
    _columns = columns.get_columns(args)
    print_response(response, args.format, args.verbose, _columns)
