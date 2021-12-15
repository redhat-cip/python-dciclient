# -*- encoding: utf-8 -*-
#
# Copyright 2015-2016 Red Hat, Inc.
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

from dciclient.v1.utils import active_string
from dciclient.v1.utils import validate_json

from dciclient.v1.api import component
from dciclient.v1.api import topic


def list(context, args):
    params = {k: getattr(args, k) for k in ["id", "sort", "limit", "offset", "where"]}
    return topic.list_components(context, **params)


def create(context, args):
    params = {
        k: getattr(args, k)
        for k in [
            "name",
            "type",
            "canonical_project_name",
            "title",
            "message",
            "url",
            "team_id",
            "topic_id",
            "state",
            "data",
            "tags",
            "released_at"
        ]
    }
    params["data"] = validate_json(context, "data", params["data"])
    params["state"] = active_string(params["state"])
    return component.create(context, **params)


def delete(context, args):
    return component.delete(context, args.id, args.etag)


def show(context, args):
    return component.get(context, args.id)


def file_upload(context, args):
    return component.file_upload(context, id=args.id, file_path=args.path)


def file_show(context, args):
    return component.file_get(context, id=args.id, file_id=args.file_id)


def file_download(context, args):
    params = {k: getattr(args, k) for k in ["id", "file_id", "target"]}
    return component.file_download(context, **params)


def file_list(context, args):
    params = {k: getattr(args, k) for k in ["id", "sort", "limit", "offset", "where"]}
    return component.file_list(context, **params)


def file_delete(context, args):
    component.file_delete(context, id=args.id, file_id=args.file_id, etag=args.etag)


def update(context, args):
    params = {
        k: getattr(args, k)
        for k in [
            "name",
            "type",
            "canonical_project_name",
            "title",
            "message",
            "url",
            "state",
            "data",
            "tags",
        ]
    }

    component_info = component.get(context, args.id)
    params["etag"] = component_info.json()["component"]["etag"]
    params["data"] = validate_json(context, "data", params["data"])
    params["state"] = active_string(params["state"])
    return component.update(context, id=args.id, **params)
