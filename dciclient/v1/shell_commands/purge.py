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
@click.option("--resource", help="Comma separated list of resource to purge.")
@click.option("--force", is_flag=True, help="Purge resources.")
@click.pass_obj
def purge(context, resource, force):
    """purge(context, resource, force)

    Purge soft-deleted resources.

    >>> dcictl purge --resource remotecis
    """

    resources = ['components', 'topics', 'tests', 'teams', 'feeders',
                 'remotecis', 'jobs', 'files', 'users', 'roles', 'products']

    l_resources = resources if resource is None else resource.split(',')

    wrong_resources = [res for res in l_resources if res not in resources]
    test_auth = base.purge(context, 'users', **{'force': False})

    if len(wrong_resources) > 0:
        msg = 'Unkown resource have been specified: %s' % wrong_resources
        if context.format == 'json':
            utils.print_json(msg)
        else:
            click.echo(msg)

    elif test_auth.status_code == 401:
        utils.format_output(test_auth, context.format)

    else:
        purged = {}
        if force:
            # If in force mode. First we retrieve the number of items to be
            # purged and then we purge them. This allows to presents meaningful
            # informations to the user that used this command.

            for res in l_resources:
                item_purged = base.purge(context, res, **{'force': False}) \
                                  .json()['_meta']['count']
                if item_purged and \
                   base.purge(context, res,
                              **{'force': True}).status_code == 204:
                    purged[res] = '%s item(s) purged' % item_purged
            if len(purged.keys()):
                utils.print_json(purged)
            else:
                utils.print_json({'message': 'No item to be purged'})
        else:
            # If not in force mode. The various endpoints are queried for the
            # informations about the resources to be purged and displayed.
            for res in l_resources:
                resource_to_delete = base.purge(context, res,
                                                **{'force': force})
                if resource_to_delete.json()['_meta']['count'] > 0:
                    purged[res] = resource_to_delete.json()
            if len(purged.keys()):
                for item in purged.keys():
                    if len(l_resources) > 1:
                        click.echo('\n%s:\n' % item)
                    utils.format_output(purged[item][item], context.format)
            else:
                utils.format_output({}, context.format)
