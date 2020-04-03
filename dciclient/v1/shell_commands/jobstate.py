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

from dciclient.v1.shell_commands import cli
from dciclient.v1 import utils

from dciclient.v1.api import jobstate


@cli.command("jobstate-list", help="List all jobstates.")
@cli.option("--sort", default="-created_at")
@cli.option("--limit", default=50)
@cli.option("--offset", default=0)
@cli.option("--where", help="An optional filter criteria.", required=False)
@cli.option("--verbose", required=False, default=False, is_flag=True)
@cli.pass_obj
def list(context, sort, limit, offset, where, verbose):
    """list(context, sort, limit, offset, where, verbose)

    List all jobstates.

    >>> dcictl jobstate-list

    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param integer offset: Offset associated with the limit
    :param string where: An optional filter criteria
    :param boolean verbose: Display verbose output
    """
    result = jobstate.list(context, sort=sort, limit=limit, offset=offset, where=where)
    utils.format_output(result, context.format, verbose=verbose)


@cli.command("jobstate-show", help="Show a jobstate.")
@cli.argument("id")
@cli.pass_obj
def show(context, id):
    """show(context, id)

    Show a jobstate.

    >>> dcictl jobstate-show [OPTIONS]

    :param string id: ID of the jobstate to show [required]
    """
    result = jobstate.get(context, id=id)
    utils.format_output(result, context.format)
