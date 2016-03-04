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

from dciclient.v1.api import jobdefinition


@cli.command("jobdefinition-list", help="List all jobdefinitions.")
@click.option("--topic_id", required=True)
@click.pass_obj
def list(context, topic_id):
    """list(context, id)

    List all jobdefinitions.

    >>> dcictl jobdefinition-list [OPTIONS]

    :param string topic_id: Topic ID [required]
    """
    result = jobdefinition.list(context, topic_id)
    utils.format_output(result, context.format,
                        jobdefinition.RESOURCE,
                        jobdefinition.TABLE_HEADERS)


@cli.command("jobdefinition-create", help="Create a jobdefinition.")
@click.option("--name", required=True)
@click.option("--test_id", required=True)
@click.option("--topic_id", required=True)
@click.option("--priority")
@click.pass_obj
def create(context, name, test_id, priority, topic_id):
    """create(context, name, test_id, priority, topic_id)

    Create a jobdefinition.

    >>> dcictl jobdefinition-create [OPTIONS]

    :param string name: Name of the jobdefinition [required]
    :param string test_id: ID of the test for this jobdefinition [required]
    :param string topic_id: ID of the topic for this jobdefinition [required]
    :param integer priority: Priority for this jobdefinition
    """
    result = jobdefinition.create(context, name=name, test_id=test_id,
                                  priority=priority, topic_id=topic_id)
    utils.format_output(result, context.format,
                        jobdefinition.RESOURCE[:-1])


@cli.command("jobdefinition-delete", help="Delete a jobdefinition.")
@click.option("--id", required=True)
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
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a jobdefinition.

    :param string id: ID of the jobdefinition to show [required]
    """
    result = jobdefinition.get(context, id=id)
    utils.format_output(result, context.format,
                        jobdefinition.RESOURCE[:-1],
                        jobdefinition.TABLE_HEADERS)


@cli.command("jobdefinition-attach-component",
             help="Attach a component to a jobdefinition.")
@click.option("--id", required=True)
@click.option("--component_id", required=True)
@click.pass_obj
def attach_component(context, id, component_id):
    """attach_component(context, id, component_id)

    Attach a component to a jobdefinition.

    >>> dcictl jobdefinition-attach-component [OPTIONS]

    :param string id: ID of the jobdefinition to attach the component to
                      [required]
    :param string component_id: ID of the component to attach [required]
    """
    result = jobdefinition.add_component(context, id=id,
                                         component_id=component_id)
    utils.format_output(result, context.format)


@cli.command("jobdefinition-unattach-component",
             help="Unattach a component to a jobdefinition.")
@click.option("--id", required=True)
@click.option("--component_id", required=True)
@click.pass_obj
def unattach_component(context, id, component_id):
    """unattach_component(context, id, component_id)

    Unattach a component from a jobdefinition.

    >>> dcictl jobdefinition-unattach-component [OPTIONS]

    :param string id: ID of the jobdefinition to unattach the component from
                      [required]
    :param string component_id: ID of the component to unattach [required]
    """
    result = jobdefinition.remove_component(context, id=id,
                                            component_id=component_id)
    if result.status_code == 204:
        unattach_msg = 'Component unattached from Jobdefinition'
        utils.print_json({'id': id,
                          'message': unattach_msg})
    else:
        utils.format_output(result, context.format)
