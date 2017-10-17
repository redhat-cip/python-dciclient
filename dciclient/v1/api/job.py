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

from dciclient.v1.api import base
from dciclient.v1.api import remoteci
from dciclient.v1.api import topic
from dciclient.v1 import utils

import json


RESOURCE = 'jobs'


def create(context, remoteci_id, topic_id, team_id=None, components=None,
           comment=None):
    job = base.create(context, RESOURCE, topic_id=topic_id,
                      remoteci_id=remoteci_id, team_id=team_id,
                      components=components, comment=comment)
    context.last_job_id = job.json()['job']['id']
    return job


def update(context, **kwargs):
    return base.update(context, RESOURCE, **kwargs)


def list(context, **kwargs):
    return base.list(context, RESOURCE, **kwargs)


def schedule(context, remoteci_id, topic_id, components=None):
    uri = '%s/%s/schedule' % (context.dci_cs_api, RESOURCE)
    data = {'remoteci_id': remoteci_id, 'topic_id': topic_id,
            'components_ids': components}
    data = utils.sanitize_kwargs(**data)
    r = context.session.post(uri, data=json.dumps(data))
    if r.status_code == 201:
        context.last_job_id = r.json()['job']['id']
    return r


def upgrade(context, job_id):
    uri = '%s/%s/upgrade' % (context.dci_cs_api, RESOURCE)
    data_json = json.dumps({'job_id': job_id})
    r = context.session.post(uri, data=data_json)
    if r.status_code == 201:
        context.last_job_id = r.json()['job']['id']
    return r


def get(context, id, **kwargs):
    return base.get(context, RESOURCE, id=id, **kwargs)


def list_results(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id,
                     subresource='results', **kwargs)


def get_full_data(context, id):
    # Get the job with embed on test and remoteci
    embed = ('topic,topic.tests,remoteci,remoteci.tests,'
             'components,rconfiguration')
    job = base.get(context, RESOURCE, id=id, embed=embed).json()['job']
    return job


def get_components(context, id):
    uri = '%s/%s/%s/components' % (context.dci_cs_api, RESOURCE, id)
    return context.session.get(uri)


def delete(context, id, etag):
    return base.delete(context, RESOURCE, id=id, etag=etag)


def list_issues(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id,
                     subresource='issues', **kwargs)


def attach_issue(context, id, url):
    uri = '%s/%s/%s/issues' % (context.dci_cs_api, RESOURCE, id)
    data_json = json.dumps({'url': url})
    return context.session.post(uri, data=data_json)


def unattach_issue(context, id, issue_id):
    return base.delete(context, RESOURCE, id,
                       subresource='issues',
                       subresource_id=issue_id)


def list_jobstates(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id,
                     subresource='jobstates', **kwargs)


def list_tests(context, id, **kwargs):
    j = base.get(context, RESOURCE, id=id, **kwargs).json()['job']
    result = {'tests': []}
    result['tests'] += topic.list_tests(
        context, j['topic_id']).json()['tests']
    result['tests'] += remoteci.list_tests(
        context, j['remoteci_id']).json()['tests']
    return result


def list_metas(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id,
                     subresource='metas', **kwargs)


def set_meta(context, id, name, value):
    uri = '%s/%s/%s/metas' % (context.dci_cs_api, RESOURCE, id)
    data_json = json.dumps({'name': name, 'value': value})
    return context.session.post(uri, data=data_json)


def get_metas(context, id, data):
    uri = '%s/%s/%s/metas' % (context.dci_cs_api, RESOURCE, id)
    return context.session.get(uri)


def delete_meta(context, id, meta_id):
    return base.delete(context, RESOURCE, id,
                       subresource='metas',
                       subresource_id=meta_id)


def notify(context, id, mesg):
    uri = '%s/%s/%s/notify' % (context.dci_cs_api, RESOURCE, id)
    data_json = json.dumps({'mesg': mesg})
    return context.session.post(uri, data=data_json)