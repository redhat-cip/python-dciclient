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

from dciclient.v1.api import component

import json


@cli.command("component-list", help="List all components.")
@click.option("--topic_id", required=True)
@click.pass_obj
def list(context, topic_id):
    """list(context, topic_id)

    List all components.

    >>> dcictl component-list [OPTIONS]

    :param string topic_id: The topic ID for the list of components to return
    """
    components = component.list(context, topic_id)
    utils.format_output(components, context.format,
                        component.RESOURCE, component.TABLE_HEADERS)


@cli.command("component-create", help="Create a component.")
@click.option("--name", required=True, help='Name of component')
@click.option("--type", required=True, help='Type of component')
@click.option("--topic_id", required=True, help='Topic ID')
@click.option("--canonical_project_name", help='Canonical project name')
@click.option("--data", default='{}', help='Data to pass (in JSON)')
@click.option("--sha", help='SHA hash')
@click.option("--title", help='Title of component')
@click.option("--message", help='Component message')
@click.option("--url", help='URL to look for the component')
@click.option("--git", help='Git reference for the component')
@click.option("--ref", help='External reference for the component')
@click.pass_obj
def create(context, name, type, canonical_project_name, data, sha,
           title, message, url, git, ref, topic_id):
    """create(context, name, type, canonical_project_name, data, sha, title,
message, url, git, ref, topic_id)

    Create a component.

    >>> dcictl component-create [OPTIONS]

    :param string name: Name of the component [required]
    :param string type: Type of the component [required]
    :param string topic_id: ID of the topic to associate with [required]
    :param string canonical_project_name: Project name
    :param json data: JSON to pass to the component
    :param string sha: SHA hash
    :param string title: Title of the component
    :param string message: Message for the component
    :param string url: URL resource to monitor
    :param string git: Git resource to monitor
    :param string ref: Reference resource to monitor
    """
    data = json.loads(data)
    result = component.create(
        context, name=name, type=type,
        canonical_project_name=canonical_project_name, data=data, sha=sha,
        title=title, message=message, url=url, git=git, ref=ref,
        topic_id=topic_id
    )
    utils.format_output(result, context.format, component.RESOURCE[:-1])


@cli.command("component-delete", help="Delete a component.")
@click.option("--id", required=True)
@click.pass_obj
def delete(context, id):
    """delete(context, id)

    Delete a component.

    >>> dcictl component-delete [OPTIONS]

    :param string id: ID of the component to delete [required]
    """
    result = component.delete(context, id=id)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Component deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("component-show", help="Show a component.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a component

    >>> dcictl component-show [OPTIONS]

    :param string id: ID of the component to show [required]
    """
    result = component.get(context, id=id)
    utils.format_output(result, context.format, component.RESOURCE[:-1],
                        component.TABLE_HEADERS)
