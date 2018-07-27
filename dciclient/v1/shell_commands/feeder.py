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

from dciclient.v1.api import feeder
from dciclient.v1.api import identity


@cli.command("feeder-list", help="List all feeders.")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list(context, sort, limit, where, verbose):
    """list(context, sort, limit, where, verbose)

    List all Feeders.

    >>> dcictl feeder-list

    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = feeder.list(context, sort=sort, limit=limit, where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("feeder-create", help="Create a feeder.")
@click.option("--name", required=True)
@click.option("--team-id", required=False)
@click.option("--data", default='{}', callback=utils.validate_json)
@click.option("--active/--no-active", default=True)
@click.pass_obj
def create(context, name, team_id, data, active):
    """create(context, name, team_id, data, active)

    Create a Feeder.

    >>> dcictl feeder-create [OPTIONS]

    :param string name: Name of the feeder [required]
    :param string team_id: ID of the team to associate this feeder with
        [required]
    :param string data: JSON data to pass during feeder creation
    :param boolean active: Mark feeder active
    :param boolean no-active: Mark feeder inactive
    """

    state = utils.active_string(active)
    team_id = team_id or identity.my_team_id(context)
    result = feeder.create(context, name=name, team_id=team_id, data=data,
                           state=state)
    utils.format_output(result, context.format)


@cli.command("feeder-update", help="Update a feeder.")
@click.argument("id")
@click.option("--etag", required=True)
@click.option("--name")
@click.option("--team-id")
@click.option("--data", callback=utils.validate_json)
@click.option("--active/--no-active", default=None)
@click.pass_obj
def update(context, id, etag, name, team_id, data, active):
    """update(context, id, etag, name, team_id, data, active)

    Update a Feeder.

    >>> dcictl feeder-update [OPTIONS]

    :param string id: ID of the feeder [required]
    :param string etag: Entity tag of the feeder resource [required]
    :param string name: Name of the feeder
    :param string team_id: ID of the team to associate this feeder with
    :param string data: JSON data to pass during feeder update
    :param boolean active: Mark feeder active
    """

    result = feeder.update(context, id=id, etag=etag, name=name,
                           team_id=team_id, data=data,
                           state=utils.active_string(active))
    utils.format_output(result, context.format)


@cli.command("feeder-delete", help="Delete a feeder.")
@click.argument("id")
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    """delete(context, id, etag)

    Delete a Feeder.

    >>> dcictl feeder-delete [OPTIONS]

    :param string id: ID of the feeder to delete [required]
    :param string etag: Entity tag of the feeder resource [required]
    """
    result = feeder.delete(context, id=id, etag=etag)

    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Feeder deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("feeder-show", help="Show a feeder.")
@click.argument("id")
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a Feeder.

    >>> dcictl feeder-show [OPTIONS]

    :param string id: ID of the feeder to show [required]
    """
    result = feeder.get(context, id=id)
    utils.format_output(result, context.format)


@cli.command("feeder-reset-api-secret", help="Reset a feeder api secret.")
@click.argument("id")
@click.option("--etag", required=True)
@click.pass_obj
def reset_api_secret(context, id, etag):
    """reset_api_secret(context, id, etag)

    Reset a Feeder api_secret.

    >>> dcictl feeder-reset-api-secret [OPTIONS]

    :param string id: ID of the feeder [required]
    :param string etag: Entity tag of the feeder resource [required]
    """
    result = feeder.reset_api_secret(context, id=id, etag=etag)
    utils.format_output(result, context.format,
                        headers=['id', 'api_secret', 'etag'])
