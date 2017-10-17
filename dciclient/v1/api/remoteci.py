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

import json


RESOURCE = 'remotecis'


def create(context, name, team_id, data={}, state='active',
           allow_upgrade_job=False):
    return base.create(context, RESOURCE, name=name, team_id=team_id,
                       data=json.dumps(data), state=state,
                       allow_upgrade_job=allow_upgrade_job)


def list(context, **kwargs):
    return base.list(context, RESOURCE, **kwargs)


def get(context, id, **kwargs):
    return base.get(context, RESOURCE, id=id, **kwargs)


def get_data(context, id, keys=None):
    return base.get_data(context, RESOURCE, id=id, keys=keys)


def update(context, id, etag, name=None, team_id=None, data=None, state=None,
           allow_upgrade_job=None):
    return base.update(context, RESOURCE, id=id, etag=etag, name=name,
                       team_id=team_id, data=data, state=state,
                       allow_upgrade_job=allow_upgrade_job)


def delete(context, id, etag):
    return base.delete(context, RESOURCE, id=id, etag=etag)


def add_test(context, id, test_id):
    uri = '%s/%s/%s/tests' % (context.dci_cs_api, RESOURCE, id)
    return context.session.post(uri, json={'test_id': test_id})


def list_tests(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id,
                     subresource='tests', **kwargs)


def remove_test(context, id, test_id):
    return base.delete(context, RESOURCE, id,
                       subresource='tests',
                       subresource_id=test_id)


def reset_api_secret(context, id, etag):
    return base.update(context, RESOURCE, id='%s/api_secret' % id, etag=etag)


def add_user(context, id, user_id):
    uri = '%s/%s/%s/users' % (context.dci_cs_api, RESOURCE, id)
    return context.session.post(uri, json={'user_id': user_id})


def list_users(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id,
                     subresource='users', **kwargs)


def remove_user(context, id, user_id):
    return base.delete(context, RESOURCE, id,
                       subresource='users',
                       subresource_id=user_id)


def add_rconfiguration(context, id, name, topic_id, component_types, data):
    uri = '%s/%s/%s/rconfigurations' % (context.dci_cs_api, RESOURCE, id)
    return context.session.post(uri, json={'name': name,
                                           'topic_id': topic_id,
                                           'component_types': component_types,
                                           'data': data})


def list_rconfigurations(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id, subresource='rconfigurations',
                     **kwargs)


def delete_rconfiguration(context, id, rconfiguration_id):
    return base.delete(context, RESOURCE, id=id,
                       subresource='rconfigurations',
                       subresource_id=rconfiguration_id)