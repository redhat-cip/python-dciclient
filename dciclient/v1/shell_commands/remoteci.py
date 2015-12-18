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

from dciclient.v1.handlers import remoteci

import json


@cli.command("remoteci-list", help="List all remotecis.")
@click.pass_obj
def list(context):
    l_remoteci = remoteci.RemoteCI(context['session'])
    utils.format_output(l_remoteci.list().json(), context['format'],
                        l_remoteci.ENDPOINT_URI, l_remoteci.TABLE_HEADERS)


@cli.command("remoteci-create", help="Create a remoteci.")
@click.option("--name", required=True)
@click.option("--team_id", required=True)
@click.option("--data", default='{}')
@click.option("--active/--no-active", default=True)
@click.pass_obj
def create(context, name, team_id, data, active):
    l_remoteci = remoteci.RemoteCI(context['session'])
    data = json.loads(data)
    utils.format_output(l_remoteci.create(name=name,
                                          team_id=team_id,
                                          data=data,
                                          active=active).json(),
                        context['format'], l_remoteci.ENDPOINT_URI[:-1])


@cli.command("remoteci-update", help="Update a remoteci.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.option("--name")
@click.option("--team_id")
@click.option("--data")
@click.option("--active/--no-active")
@click.pass_obj
def update(context, id, etag, name, team_id, data, active):
    l_remoteci = remoteci.RemoteCI(context['session'])
    result = l_remoteci.update(id=id, etag=etag, name=name, team_id=team_id,
                               data=data, active=active)

    if result.status_code == 204:
        utils.format_output({'id': id,
                             'etag': etag,
                             'name': name,
                             'active': active,
                             'message': 'Remote CI updated.'},
                            context['format'])
    else:
        utils.format_output(result.json(), context['format'])


@cli.command("remoteci-delete", help="Delete a remoteci.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    l_remoteci = remoteci.RemoteCI(context['session'])
    result = l_remoteci.delete(id=id, etag=etag)

    if result.status_code == 204:
        utils.format_output({'id': id,
                             'message': 'Remote CI deleted.'},
                            context['format'])
    else:
        utils.format_output(result.json(), context['format'])


@cli.command("remoteci-show", help="Show a remoteci.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    l_remoteci = remoteci.RemoteCI(context['session'])
    utils.format_output(l_remoteci.get(id=id).json(), context['format'],
                        l_remoteci.ENDPOINT_URI[:-1], l_remoteci.TABLE_HEADERS)
