# -*- encoding: utf-8 -*-
#
# Copyright 2016 Red Hat, Inc.
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
from dciclient.v1.api import topic

import click


@cli.command("topic-list", help="List all topics.")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list(context, sort, limit, where, verbose):
    """list(context, sort, limit. where. verbose)

    List all topics.

    >>> dcictl topic-list

    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    topics = topic.list(context, sort=sort, limit=limit, where=where)
    utils.format_output(topics, context.format, verbose=verbose)


@cli.command("topic-create", help="Create a topic.")
@click.option("--name", required=True)
@click.option("--product-id")
@click.option("--component_types", help="Component types separated by commas.")
@click.option("--active/--no-active", default=True)
@click.option("--data")
@click.pass_obj
def create(context, name, component_types, active, product_id, data):
    """create(context, name, component_types, active, product_id, data)

    Create a topic.

    >>> dcictl topic-create [OPTIONS]

    :param string name: Name of the topic [required]
    :param string component_types: list of component types separated by commas
    :param boolean active: Set the topic in the (in)active state
    :param string product_id: The product the topic belongs to
    :param string data: JSON data of the topic
    """
    if component_types:
        component_types = component_types.split(',')

    state = utils.active_string(active)
    result = topic.create(context, name=name, component_types=component_types,
                          state=state, product_id=product_id, data=data)
    utils.format_output(result, context.format)


@cli.command("topic-update", help="Update a topic.")
@click.argument("id")
@click.option("--etag", required=True)
@click.option("--name")
@click.option("--component_types", help="Component types separated by commas.")
@click.option("--label")
@click.option("--next-topic-id")
@click.option("--active/--no-active", default=None)
@click.option("--product-id")
@click.option("--data")
@click.pass_obj
def update(context, id, etag, name, component_types,
           label, next_topic_id, active, product_id, data):
    """update(context, id, etag, name, label, next_topic_id, active,
              product_id, data)

    Update a Topic.

    >>> dcictl topic-update [OPTIONS]

    :param string id: ID of the Topic [required]
    :param string etag: Entity tag of the Topic resource [required]
    :param string name: Name of the Topic
    :param string component_types: list of component types separated by commas
    :param string label: Label of the Topic
    :param string data: JSON data to pass during remote CI update
    :param boolean active: Set the topic in the active state
    :param string product_id: The product the topic belongs to
    :param string next_topic_id: The ID of the next topic for upgrades
    """

    if component_types:
        component_types = component_types.split(',')

    result = topic.update(context, id=id, etag=etag, name=name,
                          component_types=component_types,
                          label=label, next_topic_id=next_topic_id,
                          state=utils.active_string(active),
                          product_id=product_id, data=data)
    utils.format_output(result, context.format)


@cli.command("topic-delete", help="Delete a topic.")
@click.argument("id")
@click.pass_obj
def delete(context, id):
    """delete(context, id)

    Delete a topic.

    >>> dcictl topic-delete [OPTIONS]

    :param string id: ID of the topic to delete [required]
    """
    result = topic.delete(context, id=id)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Topic deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("topic-show", help="Show a topic.")
@click.argument("id")
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a topic.

    >>> dcictl topic-show [OPTIONS]

    :param string id: ID of the topic to return [required]
    """
    result = topic.get(context, id=id)
    utils.format_output(result, context.format)


@cli.command("topic-attach-team", help="Attach a team to a topic.")
@click.argument("id")
@click.option("--team-id", required=False)
@click.pass_obj
def attach_team(context, id, team_id):
    """attach_team(context, id, team_id)

    Attach a team to a topic.

    >>> dcictl topic-attach-team [OPTIONS]

    :param string id: ID of the topic to attach to [required]
    :param string team_id: ID of the team to attach to this topic [required]
    """
    team_id = team_id or identity.my_team_id(context)
    result = topic.attach_team(context, id=id, team_id=team_id)
    utils.format_output(result, context.format)


@cli.command("topic-unattach-team", help="Unattach a team from a topic.")
@click.argument("id")
@click.option("--team-id", required=False)
@click.pass_obj
def unattach_team(context, id, team_id):
    """unattach_team(context, id, team_id)

    Unattach a team from a topic.

    >>> dcictl topic-unattach-team [OPTIONS]

    :param string id: ID of the topic to unattach from [required]
    :param string team_id: ID of team to unattach from this topic,
        default is the current user team [optional]
    """
    team_id = team_id or identity.my_team_id(context)
    result = topic.unattach_team(context, id=id, team_id=team_id)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Teams has been unattached.'})
    else:
        utils.format_output(result, context.format)


@cli.command("topic-list-team", help="List teams attached to a topic.")
@click.argument("id")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list_attached_team(context, id, sort, limit, where, verbose):
    """list_attached_team(context, id, sort, limit. where. verbose)

    List teams attached to a topic.

    >>> dcictl topic-list-team

    :param string id: ID of the topic to list teams for [required]
    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = topic.list_teams(context, id=id, sort=sort, limit=limit,
                              where=where)
    utils.format_output(result, context.format, verbose=verbose)
