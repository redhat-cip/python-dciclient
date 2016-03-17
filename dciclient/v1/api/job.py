# -*- encoding: utf-8 -*-
#
# Copyright 2015 Red Hat, Inc.
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

from dciclient.v1.api import base
from dciclient.v1.api import jobdefinition

import json


RESOURCE = 'jobs'
TABLE_HEADERS = ['id', 'status', 'recheck', 'jobdefinition_id', 'remoteci_id',
                 'team_id', 'etag', 'created_at', 'updated_at']


def create(context, recheck, remoteci_id, team_id, jobdefinition_id=None):
    job = base.create(context, RESOURCE, recheck=recheck,
                      remoteci_id=remoteci_id, team_id=team_id,
                      jobdefinition_id=jobdefinition_id)
    context.last_job_id = job.json()['job']['id']
    return job


def list(context):
    return base.list(context, RESOURCE)


def schedule(context, remoteci_id, topic_id):
    uri = '%s/%s/schedule' % (context.dci_cs_api, RESOURCE)
    data_json = json.dumps({'remoteci_id': remoteci_id, 'topic_id': topic_id})
    r = context.session.post(uri, data=data_json)
    if r.status_code == 201:
        context.last_job_id = r.json()['job']['id']
    return r


def get(context, id, where=None, embed=None):
    return base.get(context, RESOURCE, id=id, where=where, embed=embed)


def get_full_data(context, id):
    # Get the job with embed on test and remoteci
    embed = 'jobdefinition,jobdefinition.test,remoteci'
    job = base.get(context, RESOURCE, id=id, embed=embed).json()['job']
    # Get the components of the jobdefinition
    jobdefinition_components = jobdefinition.get_components(
        context, job['jobdefinition']['id']).json()['components']

    # Aggregate the data of each resource
    full_data = {'remoteci': job['remoteci'],
                 'jobdefinition': job['jobdefinition'],
                 'test': job['jobdefinition']['test'],
                 'components': []}

    for component in jobdefinition_components:
        full_data['components'].append(component)

    return full_data


def delete(context, id, etag):
    return base.delete(context, RESOURCE, id=id, etag=etag)
