# -*- encoding: utf-8 -*-
#
# Copyright 2017 Red Hat, Inc.
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

from datetime import datetime
from dciclient.v1.api import context as dci_context
from dciclient.v1.api import job as dci_job
from dciclient.v1.api import topic as dci_topic
from dciclient.v1.utils import str2date

import click
import concurrent.futures
import uuid


def is_broken(j):
    url = 'https://www.distributed-ci.io/#!/jobs/%s/results' % j['id']
    jobstates = sorted(j['jobstates'], key=lambda k: k['created_at'])
    if len(jobstates) < 2:
        print('no log: ' + url)
        return True

    age = datetime.utcnow() - str2date(j['created_at'])
    begin = str2date(jobstates['created_at'])
    end = str2date(jobstates[-1]['created_at'])
    duration = end - begin

    if age.total_seconds() < 3600 * 3:
        return False
    elif duration.total_seconds() < 60 * 5:
        print('below 5 minutes: %s (duration: %s)' % (url, duration))
        return True
    elif duration.total_seconds() > 3600 * 10:
        print('above 10 hours: %s (duration: %s)' % (url, duration))
        return True
    else:
        return False


def get_topic_id(click_ctx, param, value):
    ctx = dci_context.build_dci_context()
    try:
        where = 'name:' + str(uuid.UUID(value))
    except ValueError:
        where = 'name:' + value
    topics = dci_topic.list(ctx, where=where, limit=1).json()
    if len(topics['topics']) < 1:
        raise click.BadParameter('topic "%s" not found' % value)
    return topics['topics'][0]['id']


def run(ctx, j, delete=False):
    if is_broken(j) and delete:
        dci_job.delete(ctx, id=j['id'], etag=j['etag'])


@click.command()
@click.argument('topic', callback=get_topic_id)
@click.option('--delete', is_flag=True, help='Delete the jobs.')
def main(topic, delete):
    ctx = dci_context.build_dci_context()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as e:
        for j in dci_job.iter(
                ctx,
                embed='jobdefinition,jobstates',
                where='jobdefinition.topic_id:' + topic,
                limit=100):
            e.submit(run, ctx, j, delete)


if __name__ == "__main__":
    main()
