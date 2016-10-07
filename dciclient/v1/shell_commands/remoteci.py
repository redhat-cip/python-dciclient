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

from dciclient.v1.api import remoteci
from dciclient.v1.api import user

import json


@cli.command("remoteci-list", help="List all remotecis.")
@click.pass_obj
def list(context):
    """list(context)

    List all Remote CIs

    >>> dcictl remoteci-list
    """
    result = remoteci.list(context)
    utils.format_output(result, context.format,
                        remoteci.RESOURCE, remoteci.TABLE_HEADERS)


@cli.command("remoteci-create", help="Create a remoteci.")
@click.option("--name", required=True)
@click.option("--team_id", required=False)
@click.option("--data", default='{}')
@click.option("--active/--no-active", default=True)
@click.pass_obj
def create(context, name, team_id, data, active):
    """create(context, name, team_id, data, active)

    Create a Remote CI

    >>> dcictl remoteci-create [OPTIONS]

    :param string name: Name of the Remote CI [required]
    :param string team_id: ID of the team to associate this remote CI with
        [required]
    :param string data: JSON data to pass during remote CI creation
    :param boolean active: Mark remote CI active
    :param boolean no-active: Mark remote CI inactive
    """
    team_id = team_id or user.get(context.login).json()['team_id']
    data = json.loads(data)
    result = remoteci.create(context, name=name, team_id=team_id, data=data,
                             active=active)
    utils.format_output(result, context.format, remoteci.RESOURCE[:-1])


@cli.command("remoteci-update", help="Update a remoteci.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.option("--name")
@click.option("--team_id")
@click.option("--data")
@click.option("--active/--no-active")
@click.pass_obj
def update(context, id, etag, name, team_id, data, active):
    """update(context, id, etag, name, team_id, data, active)

    Update a Remote CI.

    >>> dcictl remoteci-update [OPTIONS]

    :param string id: ID of the remote CI [required]
    :param string etag: Entity tag of the remote CI resource [required]
    :param string name: Name of the Remote CI
    :param string team_id: ID of the team to associate this remote CI with
    :param string data: JSON data to pass during remote CI update
    :param boolean active: Mark remote CI active
    :param boolean no-active: Mark remote CI inactive
    """
    result = remoteci.update(context, id=id, etag=etag, name=name,
                             team_id=team_id, data=data, active=active)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Remote CI updated.'})
    else:
        utils.format_output(result, context.format)


@cli.command("remoteci-delete", help="Delete a remoteci.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    """delete(context, id, etag)

    Delete a Remote CI.

    >>> dcictl remoteci-delete [OPTIONS]

    :param string id: ID of the remote CI to delete [required]
    :param string etag: Entity tag of the remote CI resource [required]
    """
    result = remoteci.delete(context, id=id, etag=etag)

    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Remote CI deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("remoteci-show", help="Show a remoteci.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a Remote CI.

    >>> dcictl remoteci-show [OPTIONS]

    :param string id: ID of the remote CI to show [required]
    """
    result = remoteci.get(context, id=id)
    utils.format_output(result, context.format,
                        remoteci.RESOURCE[:-1], remoteci.TABLE_HEADERS)


@cli.command("remoteci-get-data", help="Retrieve data field from a remoteci.")
@click.option("--id", required=True)
@click.option("--keys")
@click.pass_obj
def get_data(context, id, keys):
    """get_data(context, id, keys)

    Retrieve data field from a remoteci.

    >>> dcictl remoteci-get-data [OPTIONS]

    :param string id: ID of the remote CI to show [required]
    :param string id: Keys of the data field to retrieve [optional]
    """

    if keys:
        keys = keys.split(',')
    result = remoteci.get_data(context, id=id, keys=keys)
    utils.format_output(result, context.format)
