# -*- encoding: utf-8 -*-
#
# Copyright 2015-2022 Red Hat, Inc.
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

import os
import sys
from dciclient.v1.shell_commands.cli import parse_arguments
from dciclient.v1.shell_commands import columns
from dciclient.v1.shell_commands import context as dci_context
from dciclient.v1.shell_commands.runner import run
from dciclient.printer import print_response


def main():
    args = parse_arguments(sys.argv[1:], os.environ)
    context = dci_context.build_context(args)

    if not context:
        print("No credentials provided.")
        sys.exit(1)

    response = run(context, args)
    _columns = columns.get_columns(args)
    print_response(response, args.format, args.verbose, _columns)
