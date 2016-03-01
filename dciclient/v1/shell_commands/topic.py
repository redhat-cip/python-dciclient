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

import click


@cli.command("topic-list", help="List all topics.")
@click.pass_obj
def list(context):
    topics = topic.list(context)
    utils.format_output(topics, context.format,
                        topic.RESOURCE, topic.TABLE_HEADERS)


@cli.command("topic-create", help="Create a topic.")
@click.option("--name", required=True)
@click.pass_obj
def create(context, name):
    result = topic.create(context, name=name)
    utils.format_output(result, context.format, topic.RESOURCE[:-1])


@cli.command("topic-delete", help="Delete a topic.")
@click.option("--id", required=True)
@click.pass_obj
def delete(context, id):
    result = topic.delete(context, id=id)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Topic deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("topic-show", help="Show a topic.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    result = topic.get(context, id=id)
    utils.format_output(result, context.format, topic.RESOURCE[:-1],
                        topic.TABLE_HEADERS)


@cli.command("topic-attach-team", help="Attach a team to a topic.")
@click.option("--id", required=True)
@click.option("--team_id", required=True)
@click.pass_obj
def attach_team(context, id, team_id):
    result = topic.attach_team(context, id=id, team_id=team_id)
    utils.format_output(result, context.format)


@cli.command("topic-unattach-team", help="Unattach a team from a topic.")
@click.option("--id", required=True)
@click.option("--team_id", required=True)
@click.pass_obj
def unattach_team(context, id, team_id):
    result = topic.unattach_team(context, id=id, team_id=team_id)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Teams has been unattached.'})
    else:
        utils.format_output(result, context.format)


@cli.command("topic-list-team", help="List teams attached to a topic.")
@click.option("--id", required=True)
@click.pass_obj
def list_attached_team(context, id):
    result = topic.list_attached_team(context, id=id)
    utils.format_output(result, context.format,
                        team.RESOURCE, team.TABLE_HEADERS)
