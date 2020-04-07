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

from dciclient.v1.shell_commands.cli import parse_arguments
from dciclient.v1.api import user
from dciclient.v1.utils import active_string


def run(context, arguments, environment):
    args = parse_arguments(arguments, environment)
    command = args.command
    if command == "user-list":
        params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "where"]}
        return user.list(context, **params)
    if command == "user-create":
        params = {
            k: getattr(args, k)
            for k in ["name", "password", "email", "team_id", "fullname", "state"]
        }
        params["fullname"] = params["fullname"] or params["name"]
        params["state"] = active_string(params["state"])
        return user.create(context, **params)
    if command == "user-update":
        params = {
            k: getattr(args, k)
            for k in [
                "name",
                "password",
                "email",
                "team_id",
                "fullname",
                "state",
                "id",
                "etag",
            ]
        }
        params["fullname"] = params["fullname"] or params["name"]
        params["state"] = active_string(params["state"])
        return user.update(context, **params)
    if command == "user-show":
        return user.get(context, args.id)
    if command == "user-delete":
        return user.delete(context, args.id, args.etag)
