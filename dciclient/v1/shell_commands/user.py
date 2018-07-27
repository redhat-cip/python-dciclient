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

from dciclient.v1.api import identity
from dciclient.v1.api import user


@cli.command("user-list", help="List all users.")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list(context, sort, limit, where, verbose):
    """list(context, sort, limit, where, verbose)

    List all users.

    >>> dcictl user-list

    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = user.list(context, sort=sort, limit=limit, where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("user-create", help="Create a user.")
@click.option("--name", required=True)
@click.option("--password", required=True)
@click.option("--email", required=True)
@click.option("--fullname")
@click.option("--active/--no-active", default=True)
@click.option("--role-id")
@click.option("--team-id")
@click.pass_obj
def create(context, name, password, role_id, team_id, active, email, fullname):
    """create(context, name, password, role_id, team_id, active, email, fullname)

    Create a user.

    >>> dcictl user-create [OPTIONS]

    :param string name: Name of the user [required]
    :param string password: Password for the user [required]
    :param string email: Email of the user [required]
    :param string fullname: Full name of the user [optional]
    :param string role_id: ID of the role to attach this user to [optional]
    :param string team_id: ID of the team to attach this user to [optional]
    :param boolean active: Set the user in the (in)active state
    """
    team_id = team_id or identity.my_team_id(context)
    fullname = fullname or name
    result = user.create(context, name=name, password=password,
                         role_id=role_id, team_id=team_id,
                         state=utils.active_string(active),
                         email=email, fullname=fullname)
    utils.format_output(result, context.format)


@cli.command("user-update", help="Update a user.")
@click.argument("id")
@click.option("--etag", required=True)
@click.option("--name")
@click.option("--password")
@click.option("--email")
@click.option("--fullname")
@click.option("--role-id")
@click.option("--team-id")
@click.option("--active/--no-active", default=None)
@click.pass_obj
def update(context, id, etag, name, password, email, fullname, role_id,
           team_id, active):
    """update(context, id, etag, name, password, role_id, active, email, fullname)

    Update a user.

    >>> dcictl user-update [OPTIONS]

    :param string id: ID of the user to update [required]
    :param string etag: Entity tag of the user resource [required]
    :param string name: Name of the user
    :param string password: Password of the user
    :param string email: Email of the user
    :param string fullname: Full name of the user
    :param string role_id: ID of the role to attach this user to [optional]
    :param boolean active: Set the user in the active state
    """

    result = user.update(context, id=id, etag=etag, name=name,
                         password=password, role_id=role_id,
                         team_id=team_id, state=utils.active_string(active),
                         email=email, fullname=fullname)

    utils.format_output(result, context.format)


@cli.command("user-delete", help="Delete a user.")
@click.argument("id")
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
@click.argument("id")
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a user.

    >>> dcictl user-show [OPTIONS]

    :param string id: ID of the user to show [required]
    """
    result = user.get(context, id=id)
    utils.format_output(result, context.format)
