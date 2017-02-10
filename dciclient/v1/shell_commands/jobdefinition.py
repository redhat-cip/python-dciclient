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

from dciclient.v1.api import jobdefinition


@cli.command("jobdefinition-list", help="List all jobdefinitions.")
@click.option("--topic_id")
@click.pass_obj
def list(context, topic_id):
    """list(context, id)

    List all jobdefinitions.

    >>> dcictl jobdefinition-list [OPTIONS]

    :param string topic_id: Topic ID
    """
    result = jobdefinition.list(context, topic_id)
    utils.format_output(result, context.format)


@cli.command("jobdefinition-create", help="Create a jobdefinition.")
@click.option("--name", required=True)
@click.option("--topic_id", required=True)
@click.option("--priority")
@click.option("--component_types")
@click.pass_obj
def create(context, name, topic_id, priority, component_types):
    """create(context, name, priority, topic_id)

    Create a jobdefinition.

    >>> dcictl jobdefinition-create [OPTIONS]

    :param string name: Name of the jobdefinition [required]
    :param string topic_id: ID of the topic for this jobdefinition [required]
    :param integer priority: Priority for this jobdefinition
    :param string component_type: List of component type
    """
    if component_types:
        component_types = component_types.split(',')
    result = jobdefinition.create(context, name=name, priority=priority,
                                  topic_id=topic_id,
                                  component_types=component_types)
    utils.format_output(result, context.format)


@cli.command("jobdefinition-update", help="Update a jobdefinition.")
@click.argument("id")
@click.option("--etag", required=True)
@click.option("--name", required=False)
@click.option("--priority", required=False)
@click.pass_obj
def update(context, id, etag, name, priority):
    """update(context, id, etag, name)

    Update a jobdefinition.

    >>> dcictl jobdefinition-update [OPTIONS]

    :param string id: ID of the jobdefinition to update [required]
    :param string etag: Entity tag of the resource [required]
    :param string name: Name of the jobdefinition
    :param integer priority: Priority of the jobdefinition
    """
    result = jobdefinition.update(context, id=id, etag=etag, name=name,
                                  priority=priority)

    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Job Definition updated.'})
    else:
        utils.format_output(result, context.format)


@cli.command("jobdefinition-delete", help="Delete a jobdefinition.")
@click.argument("id")
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    """delete(context, id, etag)

    Delete a jobdefinition.

    >>> dcictl jobdefinition-delete [OPTIONS]

    :param string id: ID of the jobdefinition to delete [required]
    :param string etag: Entity tag of the jobdefinition resource [required]
    """
    result = jobdefinition.delete(context, id=id, etag=etag)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Job Definition deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("jobdefinition-show", help="Show a jobdefinition.")
@click.argument("id")
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a jobdefinition.

    :param string id: ID of the jobdefinition to show [required]
    """
    result = jobdefinition.get(context, id=id)
    utils.format_output(result, context.format)


@cli.command("jobdefinition-annotate", help="Annotate a jobdefinition.")
@click.argument("id")
@click.option("--comment", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def annotate(context, id, comment, etag):
    """annotate(context, id, comment, etag)

    Annotate a jobdefinition.

    >>> dcictl jobdefinition-annotate [OPTIONS]

    :param string id: ID of the jobdefinition resource [required]
    :param string comment: Comment of the jobdefinition resource [required]
    :param string etag: Entity tag of the jobdefinition resource [required]
    """
    result = jobdefinition.annotate(context, id=id, comment=comment, etag=etag)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Job Definition updated.'})
    else:
        utils.format_output(result, context.format)


@cli.command("jobdefinition-set-active", help="Annotate a jobdefinition.")
@click.argument("id")
@click.option("--active/--no-active", default=True)
@click.option("--etag", required=True)
@click.pass_obj
def setactive(context, id, active, etag):
    """setactive(context, id, active, etag)

    Change the active status of a jobdefinition.

    >>> dcictl jobdefinition-active [OPTIONS]

    :param string id: ID of the jobdefinition resource [required]
    :param boolean active: Active state of the jobdefinition resource
    :param string etag: Entity tag of the jobdefinition resource [required]
    """
    result = jobdefinition.setactive(context, id=id, active=active, etag=etag)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Job Definition updated.'})
    else:
        utils.format_output(result, context.format)


@cli.command("jobdefinition-attach-test",
             help="Attach a test to a jobdefinition.")
@click.argument("id")
@click.option("--test_id", required=True)
@click.pass_obj
def attach_test(context, id, test_id):
    """attach_test(context, id, test_id)

    Attach a test to a jobdefinition.

    >>> dcictl jobdefinition-attach-test [OPTIONS]

    :param string id: ID of the jobdefinition to attach the test to [required]
    :param string test_id: ID of the test to attach [required]
    """
    result = jobdefinition.add_test(context, id=id,
                                    test_id=test_id)
    utils.format_output(result, context.format,
                        ['jobdefinition_id', 'test_id'])


@cli.command("jobdefinition-list-test",
             help="List tests attached to a jobdefinition.")
@click.argument("id")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.pass_obj
def list_test(context, id, sort, limit):
    """list_test(context, id, test_id)

    List tests attached to a jobdefinition.

    >>> dcictl jobdefinition-list-test [OPTIONS]

    :param string id: ID of the jobdefinition to unattach the test from
                      [required]
    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    """
    result = jobdefinition.list_tests(context, id=id, sort=sort, limit=limit)
    utils.format_output(result, context.format)


@cli.command("jobdefinition-unattach-test",
             help="Unattach a test to a jobdefinition.")
@click.argument("id")
@click.option("--test_id", required=True)
@click.pass_obj
def unattach_test(context, id, test_id):
    """unattach_test(context, id, test_id)

    Unattach a test from a jobdefinition.

    >>> dcictl jobdefinition-unattach-test [OPTIONS]

    :param string id: ID of the jobdefinition to unattach the test from
                      [required]
    :param string test_id: ID of the test to unattach [required]
    """
    result = jobdefinition.remove_test(context, id=id,
                                       test_id=test_id)
    if result.status_code == 204:
        unattach_msg = 'Test unattached from Jobdefinition'
        utils.print_json({'id': id,
                          'message': unattach_msg})
    else:
        utils.format_output(result, context.format)
