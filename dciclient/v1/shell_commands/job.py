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
from dciclient.v1.api import test


@cli.command("job-list", help="List all jobs.")
@click.option("--limit", help="Number of jobs to show up.",
              required=False, default=10)
@click.pass_obj
def list(context, limit):
    """list(context)

    List all jobs.

    >>> dcictl job-list
    """
    result = job.list(
        context, limit=limit, embed='jobdefinition,remoteci,team')
    headers = ['id', 'status', 'recheck',
               'jobdefinition/name', 'remoteci/name',
               'team/name', 'etag', 'created_at', 'updated_at']

    utils.format_output(result, context.format,
                        job.RESOURCE, headers)


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
    utils.format_output(result, context.format,
                        job.RESOURCE[:-1], job.TABLE_HEADERS)


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

    Reecheck a job.

    >>> dcictl job-recheck [OPTIONS]

    :param string id: ID of the job to recheck [required]
    """
    result = job.recheck(context, id=id)
    utils.format_output(result, context.format, job.RESOURCE[:-1])


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
    """

    headers = ['filename', 'name', 'total', 'success', 'failures', 'errors',
               'skips', 'time']
    result = job.list_results(context, id=id, sort=sort, limit=limit)
    utils.format_output(result, context.format,
                        'results', headers)


@cli.command("job-attach-issue", help="Attach an issue to a job.")
@click.argument("id")
@click.option("--url", required=True)
@click.pass_obj
def attach_issue(context, id, url):
    """attach_issue(context, id, url)

    Attach an issue to a job.

    >>> dcictl job-attach-issue [OPTIONS]

    :param string id: ID of the job to attach the issue to [required]
    :param string url: URL of the issue to attach to the job[required]
    """

    result = job.attach_issue(context, id=id, url=url)
    if result.status_code == 201:
        utils.print_json({'id': id, 'message': 'Issue attached.'})
    else:
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
    :param string issue_id: ID of the issue to unattach from the job[required]
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
    """

    result = job.list_issues(context, id=id, sort=sort, limit=limit)
    headers = ['status', 'product', 'component', 'title', 'url']
    utils.format_output(result, context.format, 'issues', headers)


@cli.command("job-output", help="Show the job output.")
@click.argument('id', required=False)
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
    result = job.list_jobstates(context, id=id)
    jobstates = result.json()['jobstates']

    for js in jobstates:
        color = colors.get(js['status'], '')
        click.echo('%s[%s]\x1b[0m %s' % (
            color,
            js['status'],
            js['comment']))
        f_l = dci_file.list(
            context,
            where='jobstate_id:' + js['id'])
        for f in f_l.json()['files']:
            click.echo(dci_file.content(context, id=f['id']).text)


@cli.command("job-list-test", help="List all tests attached to a job.")
@click.argument("id")
@click.pass_obj
def list_tests(context, id):
    result = job.list_tests(context, id=id)
    utils.format_output(result, context.format, 'tests', test.TABLE_HEADERS)
