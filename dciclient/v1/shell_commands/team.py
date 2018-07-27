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

from dciclient.v1.api import team


@cli.command("team-list", help="List all teams.")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list(context, sort, limit, where, verbose):
    """list(context, sort, limit, where, verbose)

    List all teams.

    >>> dcictl team list

    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = team.list(context, sort=sort, limit=limit, where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("team-create", help="Create a team.")
@click.option("--name", required=True)
@click.option("--country")
@click.option("--active/--no-active", default=True)
@click.option("--parent-id")
@click.pass_obj
def create(context, name, country, active, parent_id):
    """create(context, name, country, active, parent_id)

    Create a team.

    >>> dcictl team-create [OPTIONS]

    :param string name: Name of the team [required]
    :param string country: Country code where the team is based
    :param boolean active: Set the team in the (in)active state
    :param string parent_id: The ID of the team this team belongs to
    """

    state = utils.active_string(active)
    result = team.create(context, name=name, country=country, state=state,
                         parent_id=parent_id)
    utils.format_output(result, context.format)


@cli.command("team-update", help="Update a team.")
@click.argument("id")
@click.option("--etag", required=True)
@click.option("--name")
@click.option("--country")
@click.option("--parent-id")
@click.option("--active/--no-active", default=None)
@click.option("--external/--no-external", default=None)
@click.pass_obj
def update(context, id, etag, name, country, parent_id, active, external):
    """update(context, id, etag, name, country, parent_id, active, external)

    Update a team.

    >>> dcictl team-update [OPTIONS]

    :param string id: ID of the team to update [required]
    :param string etag: Entity tag of the resource [required]
    :param string name: Name of the team [required]
    :param string country: Country code where the team is based
    :param boolean active: Set the team in the (in)active state
    :param string parent_id: The ID of the team this team belongs to
    :param boolean external: Set the team as external
    """

    result = team.update(context, id=id, etag=etag, name=name,
                         state=utils.active_string(active),
                         country=country, parent_id=parent_id,
                         external=external)

    utils.format_output(result, context.format)


@cli.command("team-delete", help="Delete a team.")
@click.argument("id")
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    """delete(context, id, etag)

    Delete a team

    >>> dcictl team-delete [OPTIONS]

    :param string id: ID of the team to delete [required]
    :param string etag: Entity tag of resource [required]
    """
    result = team.delete(context, id=id, etag=etag)

    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Team deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("team-show", help="Show a team.")
@click.argument("id")
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a team.

    >>> dcictl team-show [OPTIONS]

    :param string id: ID of the team [required]
    """
    result = team.get(context, id=id)
    utils.format_output(result, context.format)
