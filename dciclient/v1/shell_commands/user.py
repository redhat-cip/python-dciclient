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

from dciclient.v1.shell_commands import cli
from dciclient.v1 import utils

from dciclient.v1.api import identity
from dciclient.v1.api import user


@cli.command("user-list", help="List all users.")
@cli.option("--sort", default="-created_at")
@cli.option("--limit", default=50)
@cli.option("--offset", default=0)
@cli.option("--where", help="An optional filter criteria.", required=False)
@cli.option("--verbose", required=False, default=False, is_flag=True)
@cli.pass_obj
def list(context, sort, limit, offset, where, verbose):
    """list(context, sort, limit, offset, where, verbose)

    List all users.

    >>> dcictl user-list

    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param integer offset: Offset associated with the limit
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = user.list(context, sort=sort, limit=limit, offset=offset, where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("user-create", help="Create a user.")
@cli.option("--name", required=True)
@cli.option("--password", required=True)
@cli.option("--email", required=True)
@cli.option("--fullname")
@cli.option("--active/--no-active", default=True)
@cli.option("--team-id")
@cli.pass_obj
def create(context, name, password, team_id, active, email, fullname):
    """create(context, name, password, team_id, active, email, fullname)

    Create a user.

    >>> dcictl user-create [OPTIONS]

    :param string name: Name of the user [required]
    :param string password: Password for the user [required]
    :param string email: Email of the user [required]
    :param string fullname: Full name of the user [optional]
    :param string team_id: ID of the team to attach this user to [optional]
    :param boolean active: Set the user in the (in)active state
    """
    team_id = team_id or identity.my_team_id(context)
    fullname = fullname or name
    result = user.create(
        context,
        name=name,
        password=password,
        team_id=team_id,
        state=utils.active_string(active),
        email=email,
        fullname=fullname,
    )
    utils.format_output(result, context.format)


@cli.command("user-update", help="Update a user.")
@cli.argument("id")
@cli.option("--etag", required=True)
@cli.option("--name")
@cli.option("--password")
@cli.option("--email")
@cli.option("--fullname")
@cli.option("--team-id")
@cli.option("--active/--no-active", default=True)
@cli.pass_obj
def update(context, id, etag, name, password, email, fullname, team_id, active):
    """update(context, id, etag, name, password, email, fullname, team_id,
              active)

    Update a user.

    >>> dcictl user-update [OPTIONS]

    :param string id: ID of the user to update [required]
    :param string etag: Entity tag of the user resource [required]
    :param string name: Name of the user
    :param string password: Password of the user
    :param string email: Email of the user
    :param string fullname: Full name of the user
    :param boolean active: Set the user in the active state
    """

    result = user.update(
        context,
        id=id,
        etag=etag,
        name=name,
        password=password,
        team_id=team_id,
        state=utils.active_string(active),
        email=email,
        fullname=fullname,
    )

    utils.format_output(result, context.format)


@cli.command("user-delete", help="Delete a user.")
@cli.argument("id")
@cli.option("--etag", required=True)
@cli.pass_obj
def delete(context, id, etag):
    """delete(context, id, etag)

    Delete a user.

    >>> dcictl user-delete [OPTIONS]

    :param string id: ID of the user to delete [required]
    :param string etag: Entity tag of the user resource [required]
    """
    result = user.delete(context, id=id, etag=etag)

    if result.status_code == 204:
        utils.print_json({"id": id, "message": "User deleted."})
    else:
        utils.format_output(result, context.format)


@cli.command("user-show", help="Show a user.")
@cli.argument("id")
@cli.pass_obj
def show(context, id):
    """show(context, id)

    Show a user.

    >>> dcictl user-show [OPTIONS]

    :param string id: ID of the user to show [required]
    """
    result = user.get(context, id=id)
    utils.format_output(result, context.format)
