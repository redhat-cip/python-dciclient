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
from dciclient.v1.shell_commands import new_user as user


def run(context, arguments, environment):
    args = parse_arguments(arguments, environment)
    command = args.command
    if command == "user-list":
        return user.list(context, args)
    if command == "user-create":
        return user.create(context, args)
    if command == "user-update":
        return user.update(context, args)
    if command == "user-show":
        return user.show(context, args)
    if command == "user-delete":
        return user.delete(context, args)
