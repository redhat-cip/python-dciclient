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

from dciclient.v1.handlers import jobdefinition


@cli.command("jobdefinition-list", help="List all jobdefinitions.")
@click.pass_obj
def ct_list(dci_client):
    utils.print_json(jobdefinition.JobDefinition(dci_client).list().json())


@cli.command("jobdefinition-create", help="Create a jobdefinition.")
@click.option("--name", required=True)
@click.pass_obj
def ct_create(dci_client, name):
    utils.print_json(jobdefinition.JobDefinition(dci_client).create(name=name).json())


@cli.command("jobdefinition-update", help="Update a jobdefinition.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.option("--name", required=True)
@click.pass_obj
def ct_update(dci_client, id, etag, name):
    result = jobdefinition.JobDefinition(dci_client).update(_id=id, etag=etag, name=name)
    if result.status_code == 204:
        utils.print_json({"id": id,
                          "etag": etag,
                          "name": name,
                          "message": "JobDefinition updated."})
    else:
        utils.print_json(result.json())


@cli.command("jobdefinition-delete", help="Delete a jobdefinition.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def ct_delete(dci_client, id, etag):
    result = jobdefinition.JobDefinition(dci_client).delete(_id=id, etag=etag)
    if result.status_code == 204:
        utils.print_json({"id": id,
                          "message": "JobDefinition deleted."})
    else:
        utils.print_json(result.json())


@cli.command("jobdefinition-show", help="Show a jobdefinition.")
@click.option("--id", required=True)
@click.pass_obj
def ct_show(dci_client, id):
    result = jobdefinition.JobDefinition(dci_client).get(_id=id)
    utils.print_json(result.json())

