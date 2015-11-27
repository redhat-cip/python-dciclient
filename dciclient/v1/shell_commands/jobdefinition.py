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

from dciclient.v1.handlers import jobdefinition


@cli.command("jobdefinition-list", help="List all jobdefinitions.")
@click.pass_obj
def list(context):
    l_jobdefinition = jobdefinition.JobDefinition(context['session'])
    utils.format_output(l_jobdefinition.list().json(), context['format'],
                        l_jobdefinition.ENDPOINT_URI,
                        l_jobdefinition.TABLE_HEADERS)


@cli.command("jobdefinition-create", help="Create a jobdefinition.")
@click.option("--name", required=True)
@click.option("--test_id", required=True)
@click.option("--priority")
@click.pass_obj
def create(context, name, test_id, priority):
    l_jobdefinition = jobdefinition.JobDefinition(context['session'])
    utils.format_output(l_jobdefinition.create(name=name,
                                               test_id=test_id,
                                               priority=priority).json(),
                        context['format'], l_jobdefinition.ENDPOINT_URI[:-1])


@cli.command("jobdefinition-delete", help="Delete a jobdefinition.")
@click.option("--id", required=True)
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    l_jobdefinition = jobdefinition.JobDefinition(context['session'])
    result = l_jobdefinition.delete(id=id, etag=etag)

    if result.status_code == 204:
        utils.format_output({'id': id,
                             'message': 'Job Definition deleted.'},
                            context['format'])
    else:
        utils.format_output(result.json(), context['format'])


@cli.command("jobdefinition-show", help="Show a jobdefinition.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    l_jobdefinition = jobdefinition.JobDefinition(context['session'])
    utils.format_output(l_jobdefinition.get(id=id).json(), context['format'],
                        l_jobdefinition.ENDPOINT_URI[:-1],
                        l_jobdefinition.TABLE_HEADERS)
