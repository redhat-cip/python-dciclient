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

from dciclient.v1.utils import active_string, get_search_params
from dciclient.v1.api import team


def list(context, args):
    params = get_search_params(args)
    return team.list(context, **params)


def create(context, args):
    params = {
        k: getattr(args, k)
        for k in ["name", "country", "state", "has_pre_release_access"]
    }
    params["state"] = active_string(params["state"])
    return team.create(context, **params)


def update(context, args):
    params = {
        k: getattr(args, k)
        for k in [
            "id",
            "name",
            "country",
            "state",
            "etag",
            "external",
            "has_pre_release_access",
        ]
    }
    params["state"] = active_string(params["state"])
    return team.update(context, **params)


def delete(context, args):
    return team.delete(context, args.id, etag=args.etag)


def show(context, args):
    return team.get(context, args.id)
