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
import json

from dciclient.v1.shell_commands import cli
from dciclient.v1 import utils

from dciclient.v1.handlers import remoteci


@cli.command("remoteci-list", help="List all remotecis.")
@click.pass_obj
def list(session):
    utils.print_json(remoteci.RemoteCI(session).list().json())


@cli.command("remoteci-create", help="Create a remoteci.")
@click.option("--name", required=True)
@click.option("--team_id", required=True)
@click.option("--data", default={})
@click.pass_obj
def create(session, name, team_id, data):
    utils.print_json(remoteci.RemoteCI(session).create(name=name,
                                                       team_id=team_id,
                                                       data=json.loads(data))
                                               .json())


@cli.command("remoteci-update", help="Update a remoteci.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.option("--name")
@click.option("--team_id")
@click.option("--data")
@click.pass_obj
def update(session, id, etag, name, team_id, data):
    result = remoteci.RemoteCI(session).update(id=id, etag=etag, name=name,
                                               team_id=team_id, data=data)
    if result.status_code == 204:
        utils.print_json({"id": id,
                          "etag": etag,
                          "name": name,
                          "message": "Remote CI updated."})
    else:
        utils.print_json(result.json())


@cli.command("remoteci-delete", help="Delete a remoteci.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def delete(session, id, etag):
    result = remoteci.RemoteCI(session).delete(id=id, etag=etag)
    if result.status_code == 204:
        utils.print_json({"id": id,
                          "message": "Remote CI deleted."})
    else:
        utils.print_json(result.json())


@cli.command("remoteci-show", help="Show a remoteci.")
@click.option("--id", required=True)
@click.pass_obj
def show(session, id):
    result = remoteci.RemoteCI(session).get(id=id)
    utils.print_json(result.json())
