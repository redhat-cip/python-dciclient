# -*- encoding: utf-8 -*-
#
# Copyright 2015 Red Hat, Inc.
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
@click.pass_obj
def list(context):
    result = team.list(context)
    utils.format_output(result.json(), context.format,
                        team.RESOURCE, team.TABLE_HEADERS)


@cli.command("team-create", help="Create a team.")
@click.option("--name", required=True)
@click.pass_obj
def create(context, name):
    result = team.create(context, name=name)
    utils.format_output(result.json(), context.format, team.RESOURCE[:-1])


@cli.command("team-update", help="Update a team.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.option("--name", required=True)
@click.pass_obj
def update(context, id, etag, name):
    result = team.update(context, id=id, etag=etag, name=name)

    if result.status_code == 204:
        utils.format_output({'id': id,
                             'etag': etag,
                             'name': name,
                             'message': 'Team updated.'}, context.format)
    else:
        utils.format_output(result.json(), context.format)


@cli.command("team-delete", help="Delete a team.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    result = team.delete(context, id=id, etag=etag)

    if result.status_code == 204:
        utils.format_output({'id': id,
                             'message': 'Team deleted.'}, context.format)
    else:
        utils.format_output(result.json(), context.format)


@cli.command("team-show", help="Show a team.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    result = team.get(context, id=id)
    utils.format_output(result.json(), context.format,
                        team.RESOURCE[:-1], team.TABLE_HEADERS)
