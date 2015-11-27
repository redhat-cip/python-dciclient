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

from dciclient.v1.handlers import test


@cli.command("test-list", help="List all tests.")
@click.pass_obj
def list(context):
    l_test = test.Test(context['session'])
    utils.format_output(l_test.list().json(), context['format'],
                        l_test.endpoint_uri, l_test.table_headers)


@cli.command("test-create", help="Create a test.")
@click.option("--name", required=True)
@click.option("--data")
@click.pass_obj
def create(context, name, data):
    l_test = test.Test(context['session'])
    utils.format_output(l_test.create(name=name, data=data).json(),
                        context['format'], l_test.endpoint_uri[:-1])


@cli.command("test-update", help="Update a test.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.option("--name")
@click.option("--data")
@click.pass_obj
def update(context, id, etag, name, data):
    l_test = test.Test(context['session'])
    result = l_test.update(id=id, etag=etag, name=name, data=data)

    if result.status_code == 204:
        utils.format_output({'id': id,
                             'etag': etag,
                             'name': name,
                             'message': 'Test updated.'}, context['format'])
    else:
        utils.format_output(result.json(), context['format'])


@cli.command("test-delete", help="Delete a test.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    l_test = test.Test(context['session'])
    result = l_test.delete(id=id, etag=etag)

    if result.status_code == 204:
        utils.format_output({'id': id,
                             'message': 'Test deleted.'}, context['format'])
    else:
        utils.format_output(result.json(), context['format'])


@cli.command("test-show", help="Show a test.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    l_test = test.Test(context['session'])
    utils.format_output(l_test.get(id=id).json(), context['format'],
                        l_test.endpoint_uri[:-1], l_test.table_headers)
