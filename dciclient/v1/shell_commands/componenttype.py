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

from dciclient.v1.handlers import componenttype


@cli.command("componenttype-list", help="List all componenttypes.")
@click.pass_obj
def ct_list(dci_client):
    utils.print_json(componenttype.ComponentType(dci_client).list().json())


@cli.command("componenttype-create", help="Create a componenttype.")
@click.option("--name", required=True)
@click.pass_obj
def ct_create(dci_client, name):
    utils.print_json(componenttype.ComponentType(dci_client).create(name=name)
                     .json())


@cli.command("componenttype-update", help="Update a componenttype.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.option("--name", required=True)
@click.pass_obj
def ct_update(dci_client, id, etag, name):
    result = componenttype.ComponentType(dci_client).update(_id=id, etag=etag,
                                                            name=name)
    if result.status_code == 204:
        utils.print_json({"id": id,
                          "etag": etag,
                          "name": name,
                          "message": "ComponentType updated."})
    else:
        utils.print_json(result.json())


@cli.command("componenttype-delete", help="Delete a componenttype.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def ct_delete(dci_client, id, etag):
    result = componenttype.ComponentType(dci_client).delete(_id=id, etag=etag)
    if result.status_code == 204:
        utils.print_json({"id": id,
                          "message": "ComponentType deleted."})
    else:
        utils.print_json(result.json())


@cli.command("componenttype-show", help="Show a componenttype.")
@click.option("--id", required=True)
@click.pass_obj
def ct_show(dci_client, id):
    result = componenttype.ComponentType(dci_client).get(_id=id)
    utils.print_json(result.json())
