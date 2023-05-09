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


from dciclient.v1.api import identity
from dciclient.v1.api import remoteci


def list(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "where"]}
    return remoteci.list(context, **params)


def create(context, args):
    data = validate_json(context, "data", args.data)
    state = active_string(args.state)
    team_id = args.team_id or identity.my_team_id(context)
    return remoteci.create(
        context, name=args.name, team_id=team_id, data=data, state=state
    )


def update(context, args):
    data = validate_json(context, "data", args.data)
    state = active_string(args.state)
    return remoteci.update(
        context,
        id=args.id,
        etag=args.etag,
        name=args.name,
        team_id=args.team_id,
        data=data,
        state=state,
    )


def delete(context, args):
    return remoteci.delete(context, id=args.id, etag=args.etag)


def show(context, args):
    return remoteci.get(context, id=args.id)


def get_data(context, args):
    keys = args.keys.split(",") if args.keys else args.keys
    return remoteci.get_data(context, id=args.id, keys=keys)


def reset_api_secret(context, args):
    return remoteci.reset_api_secret(context, id=args.id, etag=args.etag)


def refresh_keys(context, args):
    return remoteci.refresh_keys(context, id=args.id, etag=args.etag)


def attach_user(context, args):
    return remoteci.add_user(context, id=args.id, user_id=args.user_id)


def list_user(context, args):
    params = {k: getattr(args, k) for k in ["id", "sort", "limit", "offset", "where"]}
    return remoteci.list_users(context, **params)


def unattach_user(context, args):
    return remoteci.remove_user(context, id=args.id, user_id=args.user_id)
