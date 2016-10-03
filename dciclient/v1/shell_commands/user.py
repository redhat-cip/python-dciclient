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

from dciclient.v1.api import user


@cli.command("user-list", help="List all users.")
@click.pass_obj
def list(context):
    """list(context)

    List all users.

    >>> dcictl user-list
    """
    result = user.list(context)
    utils.format_output(result, context.format,
                        user.RESOURCE, user.TABLE_HEADERS)


@cli.command("user-create", help="Create a user.")
@click.option("--name", required=True)
@click.option("--password", required=True)
@click.option("--role", help="'admin' or 'user'")
@click.option("--team_id", required=False)
@click.pass_obj
def create(context, name, password, role, team_id):
    """create(context, name, password, role, team_id)

    Create a user.

    >>> dcictl user-create [OPTIONS]

    :param string name: Name of the user [required]
    :param string password: Password for the user [required]
    :param string role: Role of user (admin or user)
    :param string team_id: ID of the team to attach this user to [optional]
    """
    team_id = team_id or user.get(context.login).json()['team_id']
    result = user.create(context, name=name, password=password,
                         role=role, team_id=team_id)
    utils.format_output(result, context.format, user.RESOURCE[:-1])


@cli.command("user-update", help="Update a user.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.option("--name")
@click.option("--password")
@click.option("--role", help="'admin' or 'user'")
@click.pass_obj
def update(context, id, etag, name, password, role):
    """update(context, id, etag, name, password, role)

    Update a user.

    >>> dcictl user-update [OPTIONS]

    :param string id: ID of the user to update [required]
    :param string etag: Entity tag of the user resource [required]
    :param string name: Name of the user
    :param string password: Password of the user
    :param string role: Role of the user (admin or user)
    """
    result = user.update(context, id=id, etag=etag, name=name,
                         password=password, role=role)

    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'User updated.'})
    else:
        utils.format_output(result, context.format)


@cli.command("user-delete", help="Delete a user.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    """delete(context, id, etag)

    Delete a user.

    >>> dcictl user-delete [OPTIONS]

    :param string id: ID of the user to delete [required]
    :param string etag: Entity tag of the user resource [required]
    """
    result = user.delete(context, id=id, etag=etag)

    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'User deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("user-show", help="Show a user.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a user.

    >>> dcictl user-show [OPTIONS]

    :param string id: ID of the user to show [required]
    """
    result = user.get(context, id=id)
    utils.format_output(result, context.format,
                        user.RESOURCE[:-1], user.TABLE_HEADERS)
