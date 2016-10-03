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

from dciclient.v1.api import jobstate


@cli.command("jobstate-list", help="List all jobstates.")
@click.pass_obj
def list(context):
    """list(context)

    List all jobstates.

    >>> dcictl jobstate-list
    """
    result = jobstate.list(context)
    utils.format_output(result, context.format,
                        jobstate.RESOURCE, jobstate.TABLE_HEADERS)


@cli.command("jobstate-show", help="Show a jobstate.")
@click.option("--id", required=True)
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a jobstate.

    >>> dcictl jobstate-show [OPTIONS]

    :param string id: ID of the jobstate to show [required]
    """
    result = jobstate.get(context, id=id)
    utils.format_output(result, context.format,
                        jobstate.RESOURCE[:-1], jobstate.TABLE_HEADERS)
