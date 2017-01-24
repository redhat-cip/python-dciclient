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

from dciclient.v1.api import component
from dciclient.v1.api import topic


@cli.command("component-list", help="List all components.")
@click.option("--topic_id", required=True)
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.pass_obj
def list(context, topic_id, sort, limit):
    """list(context, topic_id)

    List all components.

    >>> dcictl component-list [OPTIONS]

    :param string topic_id: The topic ID for the list of components to return
                            [required]
    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    """
    components = topic.list_components(context, id=topic_id,
                                       sort=sort, limit=limit)
    utils.format_output(components, context.format)


@cli.command("component-create", help="Create a component.")
@click.option("--name", required=True, help='Name of component')
@click.option("--type", required=True, help='Type of component')
@click.option("--canonical_project_name", help='Canonical project name')
@click.option("--data", default='{}', callback=utils.validate_json,
              help='Data to pass (in JSON)')
@click.option("--title", help='Title of component')
@click.option("--message", help='Component message')
@click.option("--url", help='URL to look for the component')
@click.option("--topic_id", required=True, help='Topic ID')
@click.option("--export_control/--no-export_control", default='true',
              help='has the export_control been done')
@click.pass_obj
def create(context, name, type, canonical_project_name, data,
           title, message, url, topic_id, export_control):
    """create(context, name, type, canonical_project_name, data, title, message, url, topic_id, export_control)  # noqa

    Create a component.

    >>> dcictl component-create [OPTIONS]

    :param string name: Name of the component [required]
    :param string type: Type of the component [required]
    :param string topic_id: ID of the topic to associate with [required]
    :param string canonical_project_name: Project name
    :param json data: JSON to pass to the component
    :param string title: Title of the component
    :param string message: Message for the component
    :param string url: URL resource to monitor
    :param boolean export_control: Set the component visible for users
    """
    result = component.create(
        context, name=name, type=type,
        canonical_project_name=canonical_project_name,
        data=data,
        title=title, message=message, url=url,
        topic_id=topic_id, export_control=export_control
    )
    utils.format_output(result, context.format)


@cli.command("component-delete", help="Delete a component.")
@click.argument("id")
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
@click.argument("id")
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a component

    >>> dcictl component-show [OPTIONS]

    :param string id: ID of the component to show [required]
    """
    result = component.get(context, id=id)
    utils.format_output(result, context.format)


@cli.command("component-status",
             help="Show an overview of the last jobs associated to this component type")  # noqa
@click.option("--type", required=True)
@click.option("--topic_id", required=True)
@click.pass_obj
def status(context, type, topic_id):
    """status(context, type, topic_id)

    Show current status of a component

    >>> dcictl component-status [OPTIONS]

    :param string type: Type of component to look up status for [required]
    :param string topic_id: The topic ID for the list of components to return
                            [required]
    """
    result = component.status(context, type=type, topic_id=topic_id)
    utils.format_output(result, context.format, 'jobs')


@cli.command("component-file-upload", help="Attach a file to a component.")
@click.argument("id")
@click.option("--path", required=True)
@click.pass_obj
def file_upload(context, id, path):
    """file_upload(context, id, path)

    Upload a file in a component

    >>> dcictl component-file-upload [OPTIONS]

    :param string id: ID of the component to attach file [required]
    :param string path: Path to the file to upload [required]
    """
    result = component.file_upload(context, id=id, file_path=path)
    utils.format_output(result, context.format)


@cli.command("component-file-show", help="Show a component file.")
@click.argument("id")
@click.option("--file_id", required=True)
@click.pass_obj
def file_show(context, id, file_id):
    """file_show(context, id, path)

    Show a component file

    >>> dcictl component-file-show [OPTIONS]

    :param string id: ID of the component to show files [required]
    :param string file_id: ID of the file to show up [required]
    """
    result = component.file_get(context, id=id, file_id=file_id)
    utils.format_output(result, context.format)


@cli.command("component-file-download", help="Retrieve a component file.")
@click.argument("id")
@click.option("--file_id", required=True)
@click.option("--target", required=True)
@click.pass_obj
def file_download(context, id, file_id, target):
    """file_download(context, id, path)

    Download a component file

    >>> dcictl component-file-download [OPTIONS]

    :param string id: ID of the component to download file [required]
    :param string file_id: ID of the component file to download [required]
    :param string target: Destination file [required]
    """
    component.file_download(context, id=id, file_id=file_id, target=target)


@cli.command("component-file-list", help="List files attached to a component.")
@click.argument("id")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.pass_obj
def file_list(context, id, sort, limit):
    """file_list(context, id, path)

    List component files

    >>> dcictl component-file-list [OPTIONS]

    :param string id: ID of the component to list files [required]
    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    """
    result = component.file_list(context, id=id, sort=sort, limit=limit)
    utils.format_output(result, context.format)


@cli.command("component-file-delete", help="Delete a component file.")
@click.argument("id")
@click.option("--file_id", required=True)
@click.pass_obj
def file_delete(context, id, file_id):
    """file_delete(context, id, path)

    Delete a component file

    >>> dcictl component-file-delete [OPTIONS]

    :param string id: ID of the component to delete file [required]
    :param string file_id: ID for the file to delete [required]
    """
    result = component.file_delete(context, id=id, file_id=file_id)
    utils.format_output(result, context.format)


@cli.command("component-update", help="Update a component.")
@click.argument("id")
@click.option("--export-control/--no-export-control")
@click.pass_obj
def update(context, id, export_control):
    """update(context, id, export_control)

    Update a component

    >>> dcictl component-update [OPTIONS]

    :param string id: ID of the component [required]
    :param boolean export-control: Set the component visible for users
    """

    component_info = component.get(context, id=id)

    etag = component_info.json()['component']['etag']
    result = component.update(context, id=id, etag=etag,
                              export_control=export_control)

    if result.status_code == 204:
        status = 'Enabled' if export_control else 'Disabled'
        utils.print_json({'id': id, 'message': 'Export Control %s.' % status})
    else:
        utils.format_output(result, context.format)
