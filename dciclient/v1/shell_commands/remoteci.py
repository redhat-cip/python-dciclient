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
from dciclient.v1.api import remoteci


@cli.command("remoteci-list", help="List all remotecis.")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list(context, sort, limit, where, verbose):
    """list(context, sort, limit, where, verbose)

    List all Remote CIs

    >>> dcictl remoteci-list

    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = remoteci.list(context, sort=sort, limit=limit, where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("remoteci-create", help="Create a remoteci.")
@click.option("--name", required=True)
@click.option("--team-id", required=False)
@click.option("--data", default='{}', callback=utils.validate_json)
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

    state = utils.active_string(active)
    team_id = team_id or identity.my_team_id(context)
    result = remoteci.create(context, name=name, team_id=team_id,
                             data=data, state=state)
    utils.format_output(result, context.format)


@cli.command("remoteci-update", help="Update a remoteci.")
@click.argument("id")
@click.option("--etag", required=True)
@click.option("--name")
@click.option("--team-id")
@click.option("--data", callback=utils.validate_json)
@click.option("--active/--no-active", default=None)
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
    """

    result = remoteci.update(context, id=id, etag=etag, name=name,
                             team_id=team_id, data=data,
                             state=utils.active_string(active))
    utils.format_output(result, context.format)


@cli.command("remoteci-delete", help="Delete a remoteci.")
@click.argument("id")
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
@click.argument("id")
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a Remote CI.

    >>> dcictl remoteci-show [OPTIONS]

    :param string id: ID of the remote CI to show [required]
    """
    result = remoteci.get(context, id=id)
    utils.format_output(result, context.format)


@cli.command("remoteci-get-data", help="Retrieve data field from a remoteci.")
@click.argument("id")
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
    utils.format_output(result, context.format, keys)


@cli.command("remoteci-attach-test",
             help="Attach a test to a remoteci.")
@click.argument("id")
@click.option("--test-id", required=True)
@click.pass_obj
def attach_test(context, id, test_id):
    """attach_test(context, id, test_id)

    Attach a test to a remoteci.

    >>> dcictl remoteci-attach-test [OPTIONS]

    :param string id: ID of the remoteci to attach the test to [required]
    :param string test_id: ID of the test to attach [required]
    """
    result = remoteci.add_test(context, id=id,
                               test_id=test_id)
    utils.format_output(result, context.format, ['remoteci_id', 'test_id'])


@cli.command("remoteci-list-test",
             help="List tests attached to a remoteci.")
@click.argument("id")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list_test(context, id, sort, limit, where, verbose):
    """list_test(context, id, sort, limit, where, verbose)

    List tests attached to a remoteci.

    >>> dcictl remoteci-list-test [OPTIONS]

    :param string id: ID of the remoteci to list the test from
                      [required]
    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = remoteci.list_tests(context, id=id, sort=sort, limit=limit,
                                 where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("remoteci-unattach-test",
             help="Unattach a test to a remoteci.")
@click.argument("id")
@click.option("--test-id", required=True)
@click.pass_obj
def unattach_test(context, id, test_id):
    """unattach_test(context, id, test_id)

    Unattach a test from a remoteci.

    >>> dcictl remoteci-unattach-test [OPTIONS]

    :param string id: ID of the remoteci to unattach the test from
                      [required]
    :param string test_id: ID of the test to unattach [required]
    """
    result = remoteci.remove_test(context, id=id,
                                  test_id=test_id)
    if result.status_code == 204:
        unattach_msg = 'Test unattached from Remoteci'
        utils.print_json({'id': id,
                          'message': unattach_msg})
    else:
        utils.format_output(result, context.format)


@cli.command("remoteci-reset-api-secret", help="Reset a remoteci api secret.")
@click.argument("id")
@click.option("--etag", required=True)
@click.pass_obj
def reset_api_secret(context, id, etag):
    """reset_api_secret(context, id, etag)

    Reset a Remote CI api_secret.

    >>> dcictl remoteci-reset-api-secret [OPTIONS]

    :param string id: ID of the remote CI [required]
    :param string etag: Entity tag of the remote CI resource [required]
    """
    result = remoteci.reset_api_secret(context, id=id, etag=etag)
    utils.format_output(result, context.format,
                        headers=['id', 'api_secret', 'etag'])


@cli.command("remoteci-refresh-keys", help="Refresh a remoteci key pair.")
@click.argument("id")
@click.option("--etag", required=True)
@click.pass_obj
def refresh_keys(context, id, etag):
    """refresh_keys(context, id, etag)

    Refresh a remoteci key pair.

    >>> dcictl remoteci-refresh-keys [OPTIONS]

    :param string id: ID of the remote CI [required]
    :param string etag: Entity tag of the remote CI resource [required]
    """
    result = remoteci.refresh_keys(context, id=id, etag=etag)
    utils.format_output(result, context.format)


@cli.command("remoteci-attach-user",
             help="Attach a user to a remoteci.")
@click.argument("id")
@click.option("--user-id", required=True)
@click.pass_obj
def attach_user(context, id, user_id):
    """attach_user(context, id, user_id)

    Attach a user to a remoteci.

    >>> dcictl remoteci-attach-user [OPTIONS]

    :param string id: ID of the remoteci to attach the user to [required]
    :param string user_id: ID of the user to attach [required]
    """
    result = remoteci.add_user(context, id=id,
                               user_id=user_id)
    utils.format_output(result, context.format, ['remoteci_id', 'user_id'])


@cli.command("remoteci-list-user",
             help="List users attached to a remoteci.")
@click.argument("id")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list_user(context, id, sort, limit, where, verbose):
    """list_user(context, id, sort, limit, where, verbose)

    List users attached to a remoteci.

    >>> dcictl remoteci-list-user [OPTIONS]

    :param string id: ID of the remoteci to list the user from
                      [required]
    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = remoteci.list_users(context, id=id, sort=sort, limit=limit,
                                 where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("remoteci-unattach-user",
             help="Unattach a user to a remoteci.")
@click.argument("id")
@click.option("--user-id", required=True)
@click.pass_obj
def unattach_user(context, id, user_id):
    """unattach_user(context, id, user_id)

    Unattach a user from a remoteci.

    >>> dcictl remoteci-unattach-user [OPTIONS]

    :param string id: ID of the remoteci to unattach the user from
                      [required]
    :param string user_id: ID of the user to unattach [required]
    """
    result = remoteci.remove_user(context, id=id,
                                  user_id=user_id)
    if result.status_code == 204:
        utils.print_json({'id': id,
                          'message': 'User unattached from RemoteCI'})
    else:
        utils.format_output(result, context.format)


@cli.command("remoteci-attach-rconfiguration", help="Create a rconfiguration.")
@click.argument("id")
@click.option("--name", required=True)
@click.option("--topic_id", required=True)
@click.option("--component_types", default='[]', callback=utils.validate_json)
@click.option("--data", default='{}', callback=utils.validate_json)
@click.pass_obj
def attach_rconfiguration(context, id, name, topic_id, component_types, data):
    """attach_rconfiguration(context, name, topic_id, component_types, data):

    Attach an rconfiguration to a Remote CI

    >>> dcictl remoteci-attach-rconfiguration ID [OPTIONS]

    :param string id: id of the remoteci
    :param string name: name of the rconfiguration [required]
    :param string topic_id: ID of the topic to associate this rconfiguration
        with [required]
    :param string component_types: list data to represent the overriden
        component_types
    :param string data: JSON data of the rconfiguration
    """

    result = remoteci.add_rconfiguration(context, id, name, topic_id,
                                         component_types, data)
    utils.format_output(result, context.format)


@cli.command("remoteci-list-rconfigurations",
             help="List rconfigurations attached to a remoteci.")
@click.argument("id")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list_rconfigurations(context, id, sort, limit, where, verbose):
    """list_rconfigurations(context, id, sort, limit, where, verbose)

    List rconfigurations attached to a remoteci.

    >>> dcictl remoteci-list-rconfigurations ID [OPTIONS]

    :param string id: ID of the remoteci to list the rconfigurations from
                      [required]
    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = remoteci.list_rconfigurations(context, id=id, sort=sort,
                                           limit=limit, where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("remoteci-unattach-rconfiguration",
             help="Unattach a rconfiguration from a remoteci.")
@click.argument("id")
@click.option("--rconfiguration-id", required=True)
@click.pass_obj
def unattach_rconfiguration(context, id, rconfiguration_id):
    """unattach_rconfiguration(context, id, rconfiguration_id):

    Unattach a rconfiguration from a remoteci.

    >>> dcictl remoteci-unattach-rconfiguration id [OPTIONS]

    :param string id: ID of the remoteci to unattach the rconfiguration from
                      [required]
    :param string rconfiguration_id: ID of the rconfiguration to unattach
                                     [required]
    """
    result = remoteci.delete_rconfiguration(
        context, id=id, rconfiguration_id=rconfiguration_id)
    if result.status_code == 204:
        utils.print_json(
            {'id': id, 'message': 'Rconfiguration unattached from RemoteCI'})
    else:
        utils.format_output(result, context.format)
