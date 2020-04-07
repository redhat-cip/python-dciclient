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
from dciclient.v1.api import test


def list(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "where"]}
    return test.list(context, **params)


def create(context, args):
    data = validate_json(context, "data", args.data)
    state = active_string(args.state)
    return test.create(context, name=args.name, data=data, state=state)


def update(context, args):
    params = {k: getattr(args, k) for k in ["id", "name", "etag", "data", "state"]}
    params["state"] = active_string(params["state"])
    return test.update(context, **params)


def delete(context, args):
    return test.delete(context, id=args.id)


def show(context, args):
    return test.get(context, id=args.id)
