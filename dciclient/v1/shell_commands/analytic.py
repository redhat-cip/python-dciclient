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

from dciclient.v1.shell_commands import cli
from dciclient.v1 import utils

from dciclient.v1.api import analytic


@cli.command("analytic-create", help="Create an analytic.")
@cli.option("--job-id", required=True)
@cli.option("--name", required=True)
@cli.option("--type", required=True)
@cli.option("--url", required=False)
@cli.option("--data", default="{}", callback=utils.validate_json)
@cli.pass_obj
def create(context, job_id, name, type, url, data):
    """create(context, job_id, name, type, url, data)

    Create an analytic.

    >>> dcictl analytic-create [OPTIONS]

    :param string job-id: The job on which to attach the analytic
    :param string name: Name of the analytic [required]
    :param string type: Type of the analytic [required]
    :param string url: Url of the bug [optional]
    :param string data: JSON data of the analytic
    """

    result = analytic.create(
        context, job_id=job_id, name=name, type=type, url=url, data=data
    )
    utils.format_output(result, context.format)


@cli.command("analytic-list", help="List analytics of a job.")
@cli.option("--job-id", required=True)
@cli.pass_obj
def list(context, job_id):
    """list(context, job_id)

    List all analytics of a job.

    >>> dcictl analytic-list [OPTIONS]

    :param string job-id: The job on which to attach the analytic
    """

    result = analytic.list(context, job_id=job_id)
    utils.format_output(result, context.format)


@cli.command("analytic-update", help="Update an analytic.")
@cli.argument("id")
@cli.option("--job-id", required=True)
@cli.option("--name", default=None)
@cli.option("--type", default=None)
@cli.option("--url", default=None)
@cli.option("--data", default=None, callback=utils.validate_json)
@cli.pass_obj
def update(context, id, job_id, name, type, url, data):
    """update(context, id, job_id, name, type, url, data)

    Update an analytic

    >>> dcictl analytic-update [OPTIONS]

    :param string job-id: The job on which to attach the analytic
    :param string name: Name of the analytic [required]
    :param string type: Type of the analytic [required]
    :param string url: Url of the bug [optional]
    :param string data: JSON data of the analytic
    """

    analytic_info = analytic.get(context, id=id, job_id=job_id)

    etag = analytic_info.json()["analytic"]["etag"]

    result = analytic.put(
        context,
        id=id,
        job_id=job_id,
        etag=etag,
        name=name,
        type=type,
        url=url,
        data=data,
    )

    utils.format_output(result, context.format)


@cli.command("analytic-show", help="Show an analytic.")
@cli.argument("id")
@cli.option("--job-id", required=True)
@cli.pass_obj
def show(context, id, job_id):
    """show(context, id, job_id)

    Show an analytic.

    >>> dcictl analytic-show [OPTIONS] id

    :param string id: The id of the analytic
    :param string job-id: The job on which to show the analytic
    """

    result = analytic.get(context, id, job_id=job_id)
    utils.format_output(result, context.format)
