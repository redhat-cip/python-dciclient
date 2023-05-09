# -*- encoding: utf-8 -*-
#
# Copyright 2017 Red Hat, Inc.
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
from dciclient.v1.api import product


def list(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "where"]}
    return product.list(context, **params)


def create(context, args):
    params = {k: getattr(args, k) for k in ["name", "label", "description", "state"]}
    params["state"] = active_string(params["state"])
    return product.create(context, **params)


def update(context, args):
    params = {
        k: getattr(args, k)
        for k in ["id", "etag", "name", "label", "description", "state"]
    }
    params["state"] = active_string(params["state"])
    return product.update(context, **params)


def delete(context, args):
    return product.delete(context, args.id, etag=args.etag)


def show(context, args):
    return product.get(context, args.id)


def attach_team(context, args):
    params = {k: getattr(args, k) for k in ["id", "team_id"]}
    return product.attach_team(context, **params)


def detach_team(context, args):
    params = {k: getattr(args, k) for k in ["id", "team_id"]}
    return product.detach_team(context, **params)


def list_teams(context, args):
    params = {k: getattr(args, k) for k in ["id", "sort", "limit", "offset", "where"]}
    return product.list_teams(context, **params)
