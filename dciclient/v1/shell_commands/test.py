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

from dciclient.v1.api import test


@cli.command("test-list", help="List all tests.")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--offset", default=0)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list(context, sort, limit, offset, where, verbose):
    """list(context, sort, limit, offset, where, verbose)

    List all tests.

    >>> dcictl test list

    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param integer offset: Offset associated with the limit
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = test.list(
        context,
        sort=sort,
        limit=limit,
        offset=offset,
        where=where
    )
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("test-create", help="Create a test.")
@click.option("--name", required=True)
@click.option("--data", callback=utils.validate_json, default='{}')
@click.option("--active/--no-active", default=True)
@click.pass_obj
def create(context, name, data, active):
    """create(context, name, data, active)

    Create a test.

    >>> dcictl test-create [OPTIONS]

    :param string name: Name of the test [required]
    :param json data: JSON formatted data block for the test
    :param boolean active: Set the test in the (in)active state
    """

    state = utils.active_string(active)
    result = test.create(context, name=name, data=data, state=state)
    utils.format_output(result, context.format)


@cli.command("test-update", help="Update a test.")
@click.argument("id")
@click.option("--etag", required=True)
@click.option("--name")
@click.option("--data", callback=utils.validate_json)
@click.option("--active/--no-active", default=None)
@click.pass_obj
def update(context, id, name, etag, data, active):
    """update(context, id, etag, name, data, active)

    Update a Test

    >>> dcictl test-update [OPTIONS]

    :param string id: ID of the Test [required]
    :param string name: Name of the Test
    :param string etag: Entity tag of the resource [required]
    :param string data: JSON data to pass during Test update
    :param boolean active: Set the test in the active state
    """

    result = test.update(context, id=id, name=name, etag=etag,
                         data=data, state=utils.active_string(active))
    utils.format_output(result, context.format)


@cli.command("test-delete", help="Delete a test.")
@click.argument("id")
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
@click.argument("id")
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a test.

    >>> dcictl test-show [OPTIONS]

    :param string id: ID of the test to return [required]
    """
    result = test.get(context, id=id)
    utils.format_output(result, context.format)
