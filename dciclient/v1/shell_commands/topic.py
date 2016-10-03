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

from dciclient.v1.api import team
from dciclient.v1.api import topic
from dciclient.v1.api import user

import click


@cli.command("topic-list", help="List all topics.")
@click.pass_obj
def list(context):
    """list(context)

    List all topics.

    >>> dcictl topic-list
    """
    topics = topic.list(context)
    utils.format_output(topics, context.format,
                        topic.RESOURCE, topic.TABLE_HEADERS)


@cli.command("topic-create", help="Create a topic.")
@click.option("--name", required=True)
@click.pass_obj
def create(context, name):
    """create(context, name)

    Create a topic.

    >>> dcictl topic-create [OPTIONS]

    :param string name: Name of the topic [required]
    """
    result = topic.create(context, name=name)
    utils.format_output(result, context.format, topic.RESOURCE[:-1])


@cli.command("topic-delete", help="Delete a topic.")
@click.option("--id", required=True)
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
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a topic.

    >>> dcictl topic-show [OPTIONS]

    :param string id: ID of the topic to return [required]
    """
    result = topic.get(context, id=id)
    utils.format_output(result, context.format, topic.RESOURCE[:-1],
                        topic.TABLE_HEADERS)


@cli.command("topic-attach-team", help="Attach a team to a topic.")
@click.option("--id", required=True)
@click.option("--team_id", required=False)
@click.pass_obj
def attach_team(context, id, team_id):
    """attach_team(context, id, team_id)

    Attach a team to a topic.

    >>> dcictl topic-attach-team [OPTIONS]

    :param string id: ID of the topic to attach to [required]
    :param string team_id: ID of the team to attach to this topic [required]
    """
    team_id = team_id or user.get(context.login).json()['team_id']
    result = topic.attach_team(context, id=id, team_id=team_id)
    utils.format_output(result, context.format)


@cli.command("topic-unattach-team", help="Unattach a team from a topic.")
@click.option("--id", required=True)
@click.option("--team_id", required=False)
@click.pass_obj
def unattach_team(context, id, team_id):
    """unattach_team(context, id, team_id)

    Unattach a team from a topic.

    >>> dcictl topic-unattach-team [OPTIONS]

    :param string id: ID of the topic to unattach from [required]
    :param string team_id: ID of team to unattach from this topic,
        default is the current user team [optional]
    """
    team_id = team_id or user.get(context.login).json()['team_id']
    result = topic.unattach_team(context, id=id, team_id=team_id)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Teams has been unattached.'})
    else:
        utils.format_output(result, context.format)


@cli.command("topic-list-team", help="List teams attached to a topic.")
@click.option("--id", required=True)
@click.pass_obj
def list_attached_team(context, id):
    """list_attached_team(context, id)

    List teams attached to a topic.

    >>> dcictl topic-list-team

    :param string id: ID of the topic to list teams for [required]
    """
    result = topic.list_attached_team(context, id=id)
    utils.format_output(result, context.format,
                        team.RESOURCE, team.TABLE_HEADERS)
