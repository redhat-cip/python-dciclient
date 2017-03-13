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

from dciclient.v1.api import file as dci_file
from dciclient.v1.api import job


@cli.command("job-list", help="List all jobs.")
@click.option("--sort", default="-created_at")
@click.option("--limit", help="Number of jobs to show up.",
              required=False, default=10)
@click.option("--where", help="An optional filter criteria.",
              required=False)
@click.pass_obj
def list(context, sort, limit, where):
    """list(context)

    List all jobs.

    >>> dcictl job-list

    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    :param string where: An optional filter criteria
    """
    result = job.list(
        context, sort=sort, limit=limit, where=where,
        embed='jobdefinition,remoteci,team')
    headers = ['id', 'status', 'recheck',
               'jobdefinition/name', 'remoteci/name',
               'team/name', 'etag', 'created_at', 'updated_at']

    utils.format_output(result, context.format, headers)


@cli.command("job-show", help="Show a job.")
@click.argument('id', required=False)
@click.pass_obj
def show(context, id):
    """show(context, id)

    Show a job.

    >>> dcictl job-show [OPTIONS]

    :param string id: ID of the job to show [required]
    """
    result = job.get(context, id=id)
    utils.format_output(result, context.format)


@cli.command("job-delete", help="Delete a job.")
@click.argument("id")
@click.option("--etag", required=True)
@click.pass_obj
def delete(context, id, etag):
    """delete(context, id, etag)

    Delete a job.

    >>> dcictl job-delete [OPTIONS]

    :param string id: ID of the job to delete [required]
    :param string etag: Entity tag of the job resource [required]
    """
    result = job.delete(context, id=id, etag=etag)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Job deleted.'})
    else:
        utils.format_output(result, context.format)


@cli.command("job-recheck", help="Recheck a job.")
@click.argument("id")
@click.pass_obj
def recheck(context, id):
    """recheck(context, id)

    Recheck a job.

    >>> dcictl job-recheck [OPTIONS]

    :param string id: ID of the job to recheck [required]
    """
    result = job.recheck(context, id=id)
    utils.format_output(result, context.format)


@cli.command("job-results", help="List all job results.")
@click.argument("id")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.pass_obj
def list_results(context, id, sort, limit):
    """list_result(context, id)

    List all job results.

    >>> dcictl job-results [OPTIONS]

    :param string id: ID of the job to recheck [required]
    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    """

    headers = ['filename', 'name', 'total', 'success', 'failures', 'errors',
               'skips', 'time']
    result = job.list_results(context, id=id, sort=sort, limit=limit)
    utils.format_output(result, context.format, headers)


@cli.command("job-attach-issue", help="Attach an issue to a job.")
@click.argument("id")
@click.option("--url", required=True)
@click.pass_obj
def attach_issue(context, id, url):
    """attach_issue(context, id, url)

    Attach an issue to a job.

    >>> dcictl job-attach-issue [OPTIONS]

    :param string id: ID of the job to attach the issue to [required]
    :param string url: URL of the issue to attach to the job [required]
    """

    result = job.attach_issue(context, id=id, url=url)
    utils.format_output(result, context.format)


@cli.command("job-unattach-issue", help="Unattach an issue from a job.")
@click.argument("id")
@click.option("--issue_id", required=True)
@click.pass_obj
def unattach_issue(context, id, issue_id):
    """unattach_issue(context, id, issue_id)

    Unattach an issue from a job.

    >>> dcictl job-unattach-issue [OPTIONS]

    :param string id: ID of the job to attach the issue to [required]
    :param string issue_id: ID of the issue to unattach from the job [required]
    """

    result = job.unattach_issue(context, id=id, issue_id=issue_id)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Issue unattached.'})
    else:
        utils.format_output(result, context.format)


@cli.command("job-list-issue", help="List all job attached issues.")
@click.argument("id")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.pass_obj
def list_issues(context, id, sort, limit):
    """list_issues(context, id)

    List all job attached issues.

    >>> dcictl job-list-issue [OPTIONS]

    :param string id: ID of the job to retrieve issues from [required]
    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    """

    result = job.list_issues(context, id=id, sort=sort, limit=limit)
    headers = ['status', 'product', 'component', 'title', 'url']
    utils.format_output(result, context.format, headers)


@cli.command("job-output", help="Show the job output.")
@click.argument('id')
@click.pass_obj
def output(context, id):
    """output(context, id)

    Show a job output.

    >>> dcictl job-output [OPTIONS]

    :param string id: ID of the job to show [required]
    """

    colors = {
        'pre-run': '\x1b[6;30;44m',
        'running': '\x1b[6;30;42m',
        'post-run': '\x1b[6;30;44m',
        'failure': '\x1b[6;30;41m'}
    result = job.list_jobstates(context, id=id, sort='created_at')
    jobstates = result.json()['jobstates']

    for js in jobstates:
        color = colors.get(js['status'], '')
        click.echo('%s[%s]\x1b[0m %s' % (
            color,
            js['status'],
            js['comment']))
        f_l = dci_file.list(
            context,
            where='jobstate_id:' + js['id'],
            sort='created_at')
        for f in f_l.json()['files']:
            click.echo(dci_file.content(context, id=f['id']).text)


@cli.command("job-list-test", help="List all tests attached to a job.")
@click.argument("id")
@click.pass_obj
def list_tests(context, id):
    """list_tests(context, id)

    List all tests attached to a job.

    >>> dcictl job-list-test [OPTIONS]

    :param string id: ID of the job [required]
    """

    result = job.list_tests(context, id=id)
    utils.format_output(result, context.format)


@cli.command("job-set-meta", help="Attach an meta to a job.")
@click.argument("id", required=True)
@click.argument("name", required=True)
@click.argument("value", required=False, default='')
@click.pass_obj
def set_meta(context, id, name, value):
    """set_meta(context, id, name, value)

    Attach an meta to a job.

    >>> dcictl job-set-meta [OPTIONS]

    :param string id: ID of the job to attach the meta to [required]
    :param string url: URL of the meta to attach to the job [required]
    :param string name: Key of the meta to attach to the job [required]
    :param string value: Value of the meta to attach to the job
    """

    result = job.set_meta(context, id=id, name=name, value=value)
    utils.format_output(result, context.format)


@cli.command("job-delete-meta", help="Drop a meta from a job.")
@click.argument("id")
@click.argument("meta_id", required=True)
@click.pass_obj
def delete_meta(context, id, meta_id):
    """delete_meta(context, id, meta_id)

    Delete an meta from a job.

    >>> dcictl job-delete-meta [OPTIONS]

    :param string id: ID of the job to attach the meta to [required]
    :param string meta_id: ID of the meta to unattach from the job [required]
    """

    result = job.delete_meta(context, id=id, meta_id=meta_id)
    if result.status_code == 204:
        utils.print_json({'id': id, 'message': 'Meta unattached.'})
    else:
        utils.format_output(result, context.format)


@cli.command("job-list-meta", help="List all job attached metas.")
@click.argument("id")
@click.option("--sort", default="-created_at")
@click.option("--limit", default=50)
@click.pass_obj
def list_metas(context, id, sort, limit):
    """list_metas(context, id)

    List all job attached metas.

    >>> dcictl job-list-meta [OPTIONS]

    :param string id: ID of the job to retrieve metas from [required]
    :param string sort: Field to apply sort
    :param integer limit: Max number of rows to return
    """

    result = job.list_metas(context, id=id, sort=sort, limit=limit)
    utils.format_output(result, context.format)
