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
@click.option("--job-id", required=True)
@click.pass_obj
def list(context, job_id):
    """list(context)

    List all files.

    >>> dcictl file-list [OPTIONS]

    :param string job_id: ID of the job [required]
    """
    result = file.list(context, where='job_id:' + job_id)
    utils.format_output(result, context.format)


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
