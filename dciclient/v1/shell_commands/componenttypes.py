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
from dciclient.v1.shell_commands import utils


@cli.command("componenttypes-list", help="List all component types.")
@click.pass_obj
def ct_list(dci_client):
    utils.print_json(dci_client.get_all_componenttypes().json())


@cli.command("componenttypes-create", help="Create a component type.")
@click.option("--name", required=True)
@click.pass_obj
def ct_create(dci_client, name):
    utils.print_json(dci_client.create_componenttype(name=name).json())


@cli.command("componenttypes-update", help="Update a component type.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.option("--name", required=True)
@click.pass_obj
def ct_update(dci_client, id, etag, name):
    result = dci_client.put_componenttype(componenttype_id=id,
                                          etag=etag, name=name)
    if result.status_code == 204:
        utils.print_json({"id": id,
                          "etag": etag,
                          "name": name,
                          "message": "Component type updated."})
    else:
        utils.print_json(result.json())


@cli.command("componenttypes-delete", help="Delete a component type.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def ct_delete(dci_client, id, etag):
    result = dci_client.delete_componenttype(componenttype_id=id, etag=etag)
    if result.status_code == 204:
        utils.print_json({"id": id,
                          "message": "Component type deleted."})
    else:
        utils.print_json(result.json())


@cli.command("componenttypes-show", help="Show a component type.")
@click.option("--id", required=True)
@click.pass_obj
def ct_show(dci_client, id):
    result = dci_client.get_componenttype(componenttype_id=id)
    utils.print_json(result.json())
