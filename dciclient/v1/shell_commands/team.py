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

from dciclient.v1.handlers import team


@cli.command("team-list", help="List all teams.")
@click.pass_obj
def list(session):
    utils.print_json(team.Team(session).list().json())


@cli.command("team-create", help="Create a team.")
@click.option("--name", required=True)
@click.pass_obj
def create(session, name):
    utils.print_json(team.Team(session).create(name=name).json())


@cli.command("team-update", help="Update a team.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.option("--name", required=True)
@click.pass_obj
def update(session, id, etag, name):
    result = team.Team(session).update(id=id, etag=etag, name=name)
    if result.status_code == 204:
        utils.print_json({"id": id,
                          "etag": etag,
                          "name": name,
                          "message": "Team updated."})
    else:
        utils.print_json(result.json())


@cli.command("team-delete", help="Delete a team.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def delete(session, id, etag):
    result = team.Team(session).delete(id=id, etag=etag)
    if result.status_code == 204:
        utils.print_json({"id": id,
                          "message": "Team deleted."})
    else:
        utils.print_json(result.json())


@cli.command("team-show", help="Show a team.")
@click.option("--id", required=True)
@click.pass_obj
def show(session, id):
    result = team.Team(session).get(id=id)
    utils.print_json(result.json())
