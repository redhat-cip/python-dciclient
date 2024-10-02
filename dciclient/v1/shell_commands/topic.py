# -*- encoding: utf-8 -*-
#
# Copyright 2016 Red Hat, Inc.
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

import json
import sys
from dciclient.v1.api import topic
from dciclient.v1.utils import active_string, get_search_params

COLUMNS = ["id", "name", "state", "export_control", "product_id", "component_types"]


def list(context, args):
    params = get_search_params(args)
    return topic.list(context, **params)


def create(context, args):
    params = {
        k: getattr(args, k)
        for k in [
            "name",
            "product_id",
            "component_types",
            "state",
            "export_control",
            "data",
        ]
    }

    if params["component_types"] is not None:
        params["component_types"] = params["component_types"].split(",")

    params["state"] = active_string(params["state"])
    return topic.create(context, **params)


def update(context, args):
    params = {
        k: getattr(args, k)
        for k in [
            "name",
            "component_types",
            "next_topic_id",
            "state",
            "export_control",
            "product_id",
            "data",
        ]
    }

    if params["component_types"] is not None:
        params["component_types"] = params["component_types"].split(",")

    params["state"] = active_string(params["state"])

    return topic.update(context, args.id, args.etag, **params)


def delete(context, args):
    return topic.delete(context, args.id, args.etag)


def show(context, args):
    return topic.get(context, args.id)


def download_pull_secret(context, args):
    topic_name = args.topic
    get_topics = topic.list(context, where=f"name:{topic_name}")
    topics = get_topics.json()["topics"]
    if len(topics) == 0:
        print(f"Topic {topic_name} does not exist.")
        sys.exit(1)
    topic_data = topics[0]["data"]
    if "pull_secret" not in topic_data:
        print(f"Topic {topic_name} doesn't have a pull secret.")
        sys.exit(1)
    with open(args.destination, "w") as f:
        pull_secret = topic_data["pull_secret"]
        json.dump(pull_secret, f)
