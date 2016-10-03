# -*- encoding: utf-8 -*-
#
# Copyright 2015-2016 Red Hat, Inc.
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
from dciclient.v1.api import test
from dciclient.v1.api import user

import json


@cli.command("test-list", help="List all tests.")
@click.option("--team_id", required=False)
@click.pass_obj
def list(context, team_id):
    """list(context, team_id)

    List all tests.

    >>> dcictl test list
    """
    team_id = team_id or user.get(context.login).json()['team_id']
    result = team.list_tests(context, team_id)
    utils.format_output(result, context.format,
                        test.RESOURCE, test.TABLE_HEADERS)


@cli.command("test-create", help="Create a test.")
@click.option("--name", required=True)
@click.option("--team_id", required=False)
@click.option("--data", default='{}')
@click.pass_obj
def create(context, name, team_id, data):
    """create(context, name, team_id, data)

    Create a test.

    >>> dcictl test-create [OPTIONS]

    :param string name: Name of the test [required]
    :param string team_id: ID of the team to associate with [required]
    :param json data: JSON formatted data block for the test
    """
    team_id = team_id or user.get(context.login).json()['team_id']
    data = json.loads(data)
    result = test.create(context, name=name, data=data, team_id=team_id)
    utils.format_output(result, context.format, test.RESOURCE[:-1])


@cli.command("test-delete", help="Delete a test.")
@click.option("--id", required=True)
@click.pass_obj
def delete(context, id):
    """delete(context, id)

    Delete a test.

    >>> dcictl test-delete [OPTIONS]

    :param string id: ID of the test to delete [required]
    """
    result = test.delete(context, id=id)

    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Test deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("test-show", help="Show a test.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a test.

    >>> dcictl test-show [OPTIONS]

    :param string id: ID of the test to return [required]
    """
    result = test.get(context, id=id)
    utils.format_output(result, context.format,
                        test.RESOURCE[:-1], test.TABLE_HEADERS)
