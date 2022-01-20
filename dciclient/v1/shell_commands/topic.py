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

from dciclient.v1.api import topic
from dciclient.v1.utils import active_string

COLUMNS = ["id", "name", "state", "export_control", "product_id", "component_types"]


def list(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "where"]}
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


def attach_team(context, args):
    return topic.attach_team(context, args.id, args.team_id)


def unattach_team(context, args):
    return topic.unattach_team(context, args.id, args.team_id)


def list_team(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "where"]}
    return topic.list_teams(context, args.id, **params)
