# -*- encoding: utf-8 -*-
#
# Copyright Red Hat, Inc.
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

from dciclient.v1.api import tag


@cli.command("tag-list", help="List all tags.")
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list(context, verbose):
    """list(context, verbose)

    List all tags.

    >>> dcictl tag-list

    :param boolean verbose: Display verbose output
    """
    result = tag.list(context)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("tag-create", help="Create a tag.")
@click.option("--name", required=True)
@click.pass_obj
def create(context, name):
    """create(context, name)

    Create a tag.

    >>> dcictl tag-create [OPTIONS]

    :param string name: Name of the tag [required]
    """

    result = tag.create(context, name=name)
    utils.format_output(result, context.format)


@cli.command("tag-delete", help="Delete a tag.")
@click.argument("id")
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    """delete(context, id, etag)

    Delete a tag

    >>> dcictl tag-delete [OPTIONS]

    :param string id: ID of the tag to delete [required]
    :param string etag: Entity tag of resource [required]
    """
    result = tag.delete(context, id=id, etag=etag)

    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Tag deleted.'})
    else:
        utils.format_output(result, context.format)
