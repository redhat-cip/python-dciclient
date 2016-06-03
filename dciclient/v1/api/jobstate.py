# -*- encoding: utf-8 -*-
#
# Copyright 2015-2016 Red Hat, Inc.
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


RESOURCE = 'jobstates'
TABLE_HEADERS = ['id', 'status', 'comment', 'job_id', 'team_id',
                 'created_at']


def create(context, status, comment, job_id):
    jobstate = base.create(context, RESOURCE, status=status, comment=comment,
                           job_id=job_id)
    json = jobstate.json()
    context.last_jobstate_id = json['jobstate']['id']
    return jobstate


def list(context, where=None, embed=None):
    return base.list(context, RESOURCE, where=where, embed=embed)


def get(context, id, where=None, embed=None):
    return base.get(context, RESOURCE, id=id, where=where, embed=embed)


def delete(context, id):
    return base.delete(context, RESOURCE, id=id)
