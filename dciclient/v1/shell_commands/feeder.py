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

from dciclient.v1.api import feeder
from dciclient.v1.utils import active_string


def list(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "where"]}
    return feeder.list(context, **params)


def create(context, args):
    params = {k: getattr(args, k) for k in ["name", "team_id", "data", "state"]}
    params["state"] = active_string(params["state"])
    return feeder.create(context, **params)


def show(context, args):
    return feeder.get(context, args.id)


def update(context, args):
    params = {
        k: getattr(args, k) for k in ["name", "team_id", "data", "state", "id", "etag"]
    }
    params["state"] = active_string(params["state"])
    return feeder.update(context, **params)


def delete(context, args):
    return feeder.delete(context, args.id, args.etag)


def reset_api_secret(context, args):
    return feeder.reset_api_secret(context, args.id, args.etag)
