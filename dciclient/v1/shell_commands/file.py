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
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list(context, sort, limit, where, verbose):
    """list(context, sort, limit, where, verbose)

    List all files.

    >>> dcictl file-list [OPTIONS]

    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = file.list(context, sort=sort, limit=limit, where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("file-show", help="Show a file.")
@click.argument("id", required=True)
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a file.

    >>> dcictl file-show [OPTIONS]

    :param string id: ID of the file to show [required]
    """
    content = file.content(context, id=id)
    click.echo(content.text)


@cli.command("file-delete", help="Delete a file.")
@click.argument("id")
@click.pass_obj
def delete(context, id):
    """delete(context, id)

    Delete a file.

    >>> dcictl file-delete [OPTIONS]

    :param string id: ID of the file to delete [required]
    """
    result = file.delete(context, id=id)

    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'File deleted.'})
    else:
        utils.format_output(result, context.format)
