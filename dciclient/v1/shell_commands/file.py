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

import click

from dciclient.v1.shell_commands import cli
from dciclient.v1 import utils

from dciclient.v1.api import file


@cli.command("file-list", help="List all files.")
@click.pass_obj
def list(context):
    """list(context)

    List all files.

    >>> dcictl file-list
    """
    result = file.list(context)
    utils.format_output(result, context.format,
                        file.RESOURCE, file.TABLE_HEADERS)


@cli.command("file-show", help="Show a file.")
@click.option("--id", required=True, help="ID of the file to show")
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a file.

    >>> dcictl file-show [OPTIONS]

    :param string id: ID of the file to show [required]
    """
    content = file.content(context, id=id)
    click.echo(content.text)
