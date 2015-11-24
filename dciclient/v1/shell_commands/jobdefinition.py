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

from dciclient.v1.handlers import jobdefinition


@cli.command("jobdefinition-list", help="List all jobdefinitions.")
@click.pass_obj
def list(session):
    utils.print_json(jobdefinition.JobDefinition(session).list().json())


@cli.command("jobdefinition-create", help="Create a jobdefinition.")
@click.option("--name", required=True)
@click.option("--test_id", required=True)
@click.option("--priority")
@click.pass_obj
def create(session, name, test_id, priority):
    utils.print_json(
        jobdefinition.JobDefinition(session)
        .create(name=name, test_id=test_id, priority=priority)
        .json()
    )


@cli.command("jobdefinition-update", help="Update a jobdefinition.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.option("--name")
@click.option("--test_id")
@click.option("--priority")
@click.pass_obj
def update(session, id, etag, name, test_id, priority):
    result = jobdefinition.JobDefinition(session).update(id=id, etag=etag,
                                                         name=name,
                                                         test_id=test_id,
                                                         priority=priority)

    if result.status_code == 204:
        utils.print_json({"id": id,
                          "etag": etag,
                          "name": name,
                          "message": "Job Definition updated."})
    else:
        utils.print_json(result.json())


@cli.command("jobdefinition-delete", help="Delete a jobdefinition.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def delete(session, id, etag):
    result = jobdefinition.JobDefinition(session).delete(id=id, etag=etag)
    if result.status_code == 204:
        utils.print_json({"id": id,
                          "message": "Job Definition deleted."})
    else:
        utils.print_json(result.json())


@cli.command("jobdefinition-show", help="Show a jobdefinition.")
@click.option("--id", required=True)
@click.pass_obj
def show(session, id):
    result = jobdefinition.JobDefinition(session).get(id=id)
    utils.print_json(result.json())
