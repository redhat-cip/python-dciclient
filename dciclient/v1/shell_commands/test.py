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

from dciclient.v1.api import test

import json


@cli.command("test-list", help="List all tests.")
@click.pass_obj
def list(context):
    result = test.list(context)
    utils.format_output(result, context.format,
                        test.RESOURCE, test.TABLE_HEADERS)


@cli.command("test-create", help="Create a test.")
@click.option("--name", required=True)
@click.option("--data", default='{}')
@click.pass_obj
def create(context, name, data):
    data = json.loads(data)
    result = test.create(context, name=name, data=data)
    utils.format_output(result, context.format, test.RESOURCE[:-1])


@cli.command("test-delete", help="Delete a test.")
@click.option("--id", required=True)
@click.pass_obj
def delete(context, id):
    result = test.delete(context, id=id)

    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Test deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("test-show", help="Show a test.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    result = test.get(context, id=id)
    utils.format_output(result, context.format,
                        test.RESOURCE[:-1], test.TABLE_HEADERS)
