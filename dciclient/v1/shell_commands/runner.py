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
from dciclient.v1.shell_commands.context import get_context
from dciclient.v1.api import user
from dciclient.v1 import utils


def run(arguments, environment):
    args = parse_arguments(arguments, environment)
    context = get_context(args)

    command = args.command
    result = None
    if command == "user_list":
        params = {k: args[k] for k in ["sort", "limit", "offset", "where", "verbose"]}
        result = user.list(context, **params)

    return utils.format_output(result, args.format, verbose=args.verbose)
