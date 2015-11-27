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

from dciclient.v1.handlers import component


@cli.command("component-list", help="List all components.")
@click.pass_obj
def list(context):
    l_component = component.Component(context['session'])
    utils.format_output(l_component.list().json(), context['format'],
                        l_component.endpoint_uri, l_component.table_headers)


@cli.command("component-create", help="Create a component.")
@click.option("--name", required=True)
@click.option("--componenttype_id", required=True)
@click.option("--canonical_project_name")
@click.option("--data")
@click.option("--sha")
@click.option("--title")
@click.option("--message")
@click.option("--url")
@click.option("--git")
@click.option("--ref")
@click.pass_obj
def create(context, name, componenttype_id, canonical_project_name, data, sha,
           title, message, url, git, ref):
    l_component = component.Test(context['session'])
    utils.format_output(
        l_component
        .create(name=name, componenttype_id=componenttype_id,
                canonical_project_name=canonical_project_name, data=data,
                sha=sha, title=title, message=message, url=url, git=git,
                ref=ref)
        .json(), context['format'], l_component.endpoint_uri[:-1]
    )


@cli.command("component-delete", help="Delete a component.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    l_component = component.Component(context['session'])
    result = l_component.delete(id=id, etag=etag)
    if result.status_code == 204:
        utils.format_output({'id': id,
                             'message': 'Component deleted.'},
                            context['format'])
    else:
        utils.format_output(result.json(), context['format'])


@cli.command("component-show", help="Show a component.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    l_component = component.Component(context['session'])
    utils.format_output(l_component.get(id=id).json(),
                        context['format'],
                        l_component.endpoint_uri[:-1],
                        l_component.table_headers)
