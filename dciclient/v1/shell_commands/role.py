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

from dciclient.v1.api import role


@cli.command("role-list", help="List all roles.")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list(context, sort, limit, where, verbose):
    """list(context, sort, limit, where, verbose)

    List all roles.

    >>> dcictl role list

    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = role.list(context, sort=sort, limit=limit, where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("role-create", help="Create a role.")
@click.option("--name", required=True)
@click.option("--label", required=False)
@click.option("--description", required=False)
@click.option("--active/--no-active", default=True)
@click.pass_obj
def create(context, name, label, description, active):
    """create(context, name, label, description, active)

    Create a role.

    >>> dcictl role-create [OPTIONS]

    :param string name: Name of the role [required]
    :param string label: Label of the role [optional]
    :param string description: Description of the role [optional]
    :param boolean active: Set the role in the (in)active state
    """

    state = utils.active_string(active)
    result = role.create(context, name=name, label=label,
                         description=description, state=state)
    utils.format_output(result, context.format)


@cli.command("role-update", help="Update a role.")
@click.argument("id")
@click.option("--etag", required=True)
@click.option("--name", required=False)
@click.option("--description", required=False)
@click.option("--active/--no-active", default=None)
@click.pass_obj
def update(context, id, etag, name, description, active):
    """update(context, id, etag, name, description, active)

    Update a role.

    >>> dcictl role-update [OPTIONS]

    :param string id: ID of the role to update [required]
    :param string etag: Entity tag of the resource [required]
    :param string name: New name of the role [required]
    :param string description: New description of the role [required]
    :param boolean active: Set the role in the active state
    """

    result = role.update(context, id=id, etag=etag, name=name,
                         description=description,
                         state=utils.active_string(active))

    utils.format_output(result, context.format)


@cli.command("role-delete", help="Delete a role.")
@click.argument("id")
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    """delete(context, id, etag)

    Delete a role.

    >>> dcictl role-delete [OPTIONS]

    :param string id: ID of the role to delete [required]
    :param string etag: Entity tag of resource [required]
    """
    result = role.delete(context, id=id, etag=etag)

    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Role deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("role-show", help="Show a role.")
@click.argument("id")
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a role.

    >>> dcictl role-show [OPTIONS]

    :param string id: ID of the role to return [required]
    """
    result = role.get(context, id=id)
    utils.format_output(result, context.format)
