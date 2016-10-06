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
from dciclient.v1 import utils


RESOURCE = 'files'
TABLE_HEADERS = ['id', 'name', 'mime', 'md5', 'jobstate_id',
                 'team_id', 'created_at']


def create(context, name, content, mime='text/plain',
           jobstate_id=None, md5=None, job_id=None):
    headers = {'DCI-NAME': name,
               'DCI-MIME': mime,
               'DCI-JOBSTATE-ID': jobstate_id,
               'DCI-MD5': md5,
               'DCI-JOB-ID': job_id}
    headers = utils.sanitize_kwargs(**headers)
    uri = '%s/%s' % (context.dci_cs_api, RESOURCE)
    return context.session.post(uri, headers=headers, data=content)


def get(context, id, where=None, embed=None):
    return base.get(context, RESOURCE, id=id, where=where, embed=embed)


def list(context, where=None, embed=None):
    return base.list(context, RESOURCE, where=where, embed=embed)


def delete(context, id):
    return base.delete(context, RESOURCE, id=id)


def content(context, id):
    uri = '%s/%s/%s/content' % (context.dci_cs_api, RESOURCE, id)
    r = context.session.get(uri)
    return r
