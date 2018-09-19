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
@click.option("--topic-id", required=True)
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def list(context, topic_id, sort, limit, where, verbose):
    """list(context, topic_id, sort, limit, where, verbose)

    List all components.

    >>> dcictl component-list [OPTIONS]

    :param string topic_id: The topic ID for the list of components to return
                            [required]
    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    components = topic.list_components(context, id=topic_id,
                                       sort=sort, limit=limit, where=where)
    utils.format_output(components, context.format, verbose=verbose)


@cli.command("component-create", help="Create a component.")
@click.option("--name", required=True, help='Name of component')
@click.option("--type", required=True, help='Type of component')
@click.option("--canonical_project_name", help='Canonical project name')
@click.option("--data", default='{}', callback=utils.validate_json,
              help='Data to pass (in JSON)')
@click.option("--title", help='Title of component')
@click.option("--message", help='Component message')
@click.option("--url", help='URL to look for the component')
@click.option("--topic-id", required=True, help='Topic ID')
@click.option("--export_control/--no-export_control", default='true',
              help='has the export_control been done')
@click.option("--active/--no-active", default=True)
@click.pass_obj
def create(context, name, type, canonical_project_name, data,
           title, message, url, topic_id, export_control, active):
    """create(context, name, type, canonical_project_name, data, title, message, url, topic_id, export_control, active)  # noqa

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
    :param boolean active: Set the component in the (in)active state
    """

    state = utils.active_string(active)
    result = component.create(
        context, name=name, type=type,
        canonical_project_name=canonical_project_name,
        data=data,
        title=title, message=message, url=url,
        topic_id=topic_id, export_control=export_control,
        state=state
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
@click.option("--file-id", required=True)
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
@click.option("--file-id", required=True)
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
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.option("--long", "--verbose", "verbose",
              required=False, default=False, is_flag=True)
@click.pass_obj
def file_list(context, id, sort, limit, where, verbose):
    """file_list(context, id, path)

    List component files

    >>> dcictl component-file-list [OPTIONS]

    :param string id: ID of the component to list files [required]
    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = component.file_list(context, id=id, sort=sort, limit=limit,
                                 where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("component-file-delete", help="Delete a component file.")
@click.argument("id")
@click.option("--file-id", required=True)
@click.pass_obj
def file_delete(context, id, file_id):
    """file_delete(context, id, path)

    Delete a component file

    >>> dcictl component-file-delete [OPTIONS]

    :param string id: ID of the component to delete file [required]
    :param string file_id: ID for the file to delete [required]
    """
    component.file_delete(context, id=id, file_id=file_id)


@cli.command("component-update", help="Update a component.")
@click.argument("id")
@click.option("--export-control/--no-export-control", default=None)
@click.option("--active/--no-active", default=None)
@click.pass_obj
def update(context, id, export_control, active):
    """update(context, id, export_control, active)

    Update a component

    >>> dcictl component-update [OPTIONS]

    :param string id: ID of the component [required]
    :param boolean export-control: Set the component visible for users
    :param boolean active: Set the component in the active state
    """

    component_info = component.get(context, id=id)

    etag = component_info.json()['component']['etag']

    result = component.update(context, id=id, etag=etag,
                              export_control=export_control,
                              state=utils.active_string(active))

    utils.format_output(result, context.format)


@cli.command("component-attach-issue", help="Attach an issue to a component.")
@click.argument("id")
@click.option("--url", required=True)
@click.pass_obj
def attach_issue(context, id, url):
    """attach_issue(context, id, url)

    Attach an issue to a component.

    >>> dcictl component-attach-issue [OPTIONS]

    :param string id: ID of the component to attach the issue to [required]
    :param string url: URL of the issue to attach to the component[required]
    """

    result = component.attach_issue(context, id=id, url=url)
    if result.status_code == 201:
        utils.print_json({'id': id, 'message': 'Issue attached.'})
    else:
        utils.format_output(result, context.format)


@cli.command("component-unattach-issue",
             help="Unattach an issue from a component.")
@click.argument("id")
@click.option("--issue-id", required=True)
@click.pass_obj
def unattach_issue(context, id, issue_id):
    """unattach_issue(context, id, issue_id)

    Unattach an issue from a component.

    >>> dcictl component-unattach-issue [OPTIONS]

    :param string id: ID of the component to unattach the issue from [required]
    :param string issue_id: ID of the issue to unattach from the component[required]  # noqa
    """

    result = component.unattach_issue(context, id=id, issue_id=issue_id)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Issue unattached.'})
    else:
        utils.format_output(result, context.format)


@cli.command("component-list-issue",
             help="List all component attached issues.")
@click.argument("id")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.pass_obj
def list_issues(context, id, sort, limit):
    """list_issues(context, id)

    List all component attached issues.

    >>> dcictl component-list-issue [OPTIONS]

    :param string id: ID of the component to retrieve issues from [required]
    """

    result = component.list_issues(context, id=id, sort=sort, limit=limit)
    headers = ['id', 'status', 'product', 'component', 'title', 'url']
    utils.format_output(result, context.format, headers)
