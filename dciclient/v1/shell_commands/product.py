# -*- encoding: utf-8 -*-
#
# Copyright 2017 Red Hat, Inc.
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

from dciclient.v1.api import product


@cli.command("product-list", help="List all products.")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list(context, sort, limit, where, verbose):
    """list(context, sort, limit, where, verbose)

    List all products.

    >>> dcictl product list

    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = product.list(context, sort=sort, limit=limit, where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("product-create", help="Create a product.")
@click.option("--name", required=True)
@click.option("--team-id", required=True)
@click.option("--label", required=False)
@click.option("--description", required=False)
@click.option("--active/--no-active", default=True)
@click.pass_obj
def create(context, name, label, description, active, team_id):
    """create(context, name, label, description, active, team_id)

    Create a product.

    >>> dcictl product-create [OPTIONS]

    :param string name: Name of the product [required]
    :param string label: Label of the product [optional]
    :param string description: Description of the product [optional]
    :param boolean active: Set the product in the (in)active state
    :param string team_id: Team the product belongs to [required]
    """

    state = utils.active_string(active)
    result = product.create(context, name=name, team_id=team_id,
                            label=label, description=description, state=state)
    utils.format_output(result, context.format)


@cli.command("product-update", help="Update a product.")
@click.argument("id")
@click.option("--etag", required=True)
@click.option("--name", required=False)
@click.option("--description", required=False)
@click.option("--active/--no-active", default=None)
@click.option("--team-id", required=False)
@click.pass_obj
def update(context, id, etag, name, description, active, team_id):
    """update(context, id, etag, name, description, active, team_id)

    Update a product.

    >>> dcictl product-update [OPTIONS]

    :param string id: ID of the product to update [required]
    :param string etag: Entity tag of the resource [required]
    :param string name: New name of the product [required]
    :param string description: New description of the product [required]
    :param boolean active: Set the product in the active state
    :param string team_id: Team the product belongs to [required]
    """

    result = product.update(context, id=id, etag=etag, name=name,
                            description=description,
                            state=utils.active_string(active),
                            team_id=team_id)

    utils.format_output(result, context.format)


@cli.command("product-delete", help="Delete a product.")
@click.argument("id")
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    """delete(context, id, etag)

    Delete a product.

    >>> dcictl product-delete [OPTIONS]

    :param string id: ID of the product to delete [required]
    :param string etag: Entity tag of resource [required]
    """
    result = product.delete(context, id=id, etag=etag)

    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Product deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("product-show", help="Show a product.")
@click.argument("id")
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a product.

    >>> dcictl product-show [OPTIONS]

    :param string id: ID of the product to return [required]
    """
    result = product.get(context, id=id)
    utils.format_output(result, context.format)
