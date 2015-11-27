# -*- encoding: utf-8 -*-
#
# Copyright 2015 Red Hat, Inc.
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

import click

from dciclient.v1.shell_commands import cli
from dciclient.v1 import utils

from dciclient.v1.handlers import file


@cli.command("file-list", help="List all files.")
@click.pass_obj
def list(context):
    l_file = file.File(context['session'])
    utils.format_output(l_file.list().json(), context['format'],
                        l_file.endpoint_uri, l_file.table_headers)


@cli.command("file-show", help="Show a file.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    l_file = file.File(context['session'])
    utils.format_output(l_file.get(id=id).json(), context['format'],
                        l_file.endpoint_uri[:-1], l_file.table_headers)
