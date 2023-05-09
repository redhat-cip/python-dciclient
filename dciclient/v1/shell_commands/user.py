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

from dciclient.v1.api import user
from dciclient.v1.utils import active_string

COLUMNS = ["id", "created_at", "updated_at", "etag", "name",
           "sso_username", "fullname", "email", "password",
           "timezone", "state"]


def list(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "where"]}
    return user.list(context, **params)


def create(context, args):
    params = {
        k: getattr(args, k)
        for k in ["name", "password", "email", "fullname", "state"]
    }
    params["fullname"] = params["fullname"] or params["name"]
    params["state"] = active_string(params["state"])
    return user.create(context, **params)


def show(context, args):
    return user.get(context, args.id)


def update(context, args):
    params = {
        k: getattr(args, k)
        for k in [
            "name",
            "password",
            "email",
            "fullname",
            "state",
            "id",
            "etag",
        ]
    }
    params["fullname"] = params["fullname"] or params["name"]
    params["state"] = active_string(params["state"])
    return user.update(context, **params)


def delete(context, args):
    return user.delete(context, args.id, args.etag)
