# -*- encoding: utf-8 -*-
#
# Copyright 2015-2017 Red Hat, Inc.
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

from dciclient.v1.api import base


@cli.command("purge", help="Purge soft-deleted resources.")
@click.option("--resource", help="Type of resource to purge.")
@click.option("--noop", is_flag=True, help="Show resource to purge.")
@click.pass_obj
def purge(context, resource, noop):
    """purge(context, resource, noop)

    Purge soft-deleted resources.

    >>> dcictl purge --resource remoteci
    """

    resources = ['components', 'topics', 'tests', 'teams', 'jobdefinitions',
                 'remotecis', 'jobs', 'files', 'component_files', 'users']

    l_resources = resources if resource is None else resource.split(',')

    for res in l_resources:
        if res not in resources:
            click.echo('%s; is an invalid resource' % res)
        else:
            kwargs = {'noop': noop}
            resource_to_delete = base.purge(context, res, **kwargs)
            if noop:
                if len(l_resources) > 1:
                    click.echo('\n%s:\n' % res)
                utils.format_output(resource_to_delete, context.format)
            elif resource_to_delete.status_code == 204:
                utils.print_json({'message': 'Resources purged.'})
