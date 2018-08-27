# -*- encoding: utf-8 -*-
#
# Copyright Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import click

from dciclient.v1.shell_commands import cli
from dciclient.v1 import utils

from dciclient.v1.api import analytic


@cli.command("analytic-create", help="Create an analytic.")
@click.option("--name", required=True)
@click.option("--type", required=True)
@click.option("--url", required=False)
@click.option("--data", default='{}', callback=utils.validate_json)
@click.pass_obj
def create(context, name, type, url, data):
    """create(context, name, type, url, data)

    Create an analytic.

    >>> dcictl analytic-create [OPTIONS]

    :param string name: Name of the analytic [required]
    :param string type: Type of the analytic [required]
    :param string url: Url of the bug [optional]
    :param string data: JSON data of the analytic
    """

    #state = utils.active_string(active)
    result = analytic.create(context, name=name, type=type,
                             url=url, data=data)
    utils.format_output(result, context.format)
