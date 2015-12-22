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
@click.pass_obj
def list(context):
    components = component.list(context).json()
    utils.format_output(components, context.format,
                        component.RESOURCE, component.TABLE_HEADERS)


@cli.command("component-create", help="Create a component.")
@click.option("--name", required=True)
@click.option("--type", required=True)
@click.option("--canonical_project_name")
@click.option("--data", default='{}')
@click.option("--sha")
@click.option("--title")
@click.option("--message")
@click.option("--url")
@click.option("--git")
@click.option("--ref")
@click.pass_obj
def create(context, name, type, canonical_project_name, data, sha,
           title, message, url, git, ref):
    data = json.loads(data)
    result = component.create(
        context, name=name, type=type,
        canonical_project_name=canonical_project_name, data=data, sha=sha,
        title=title, message=message, url=url, git=git, ref=ref
    ).json()
    utils.format_output(result, context.format, component.RESOURCE[:-1])


@cli.command("component-delete", help="Delete a component.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    result = component.delete(context, id=id, etag=etag)
    if result.status_code == 204:
        utils.format_output({'id': id, 'message': 'Component deleted.'},
                            context.format)
    else:
        utils.format_output(result.json(), context.format)


@cli.command("component-show", help="Show a component.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    result = component.get(context, id=id).json()
    utils.format_output(result, context.format, component.RESOURCE[:-1],
                        component.TABLE_HEADERS)
