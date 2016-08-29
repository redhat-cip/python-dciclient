# -*- encoding: utf-8 -*-
#
# Copyright 2016 Red Hat, Inc.
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


RESOURCE = 'topics'
TABLE_HEADERS = ['id', 'name', 'etag', 'created_at', 'updated_at']


def create(context, name):
    return base.create(context, RESOURCE, name=name)


def list(context):
    return base.list(context, RESOURCE)


def get(context, id, where=None, embed=None):
    return base.get(context, RESOURCE, id=id, where=where, embed=embed)


def delete(context, id):
    return base.delete(context, RESOURCE, id=id)


def attach_team(context, id, team_id):
    uri = '%s/%s/%s/teams' % (context.dci_cs_api, RESOURCE, id)
    return context.session.post(uri, json={'team_id': team_id})


def unattach_team(context, id, team_id):
    uri = '%s/%s/%s/teams/%s' % (context.dci_cs_api, RESOURCE, id, team_id)
    return context.session.delete(uri)


def list_attached_team(context, id):
    uri = '%s/%s/%s/teams' % (context.dci_cs_api, RESOURCE, id)
    return context.session.get(uri)


def list_components(context, id):
    return base.list(context, RESOURCE, id=id, subresource='components')


def get_jobs_from_components(context, topic_id, component_id):
    uri = '%s/%s/%s/components/%s/jobs' % \
          (context.dci_cs_api, RESOURCE, topic_id, component_id)
    return context.session.get(uri)
