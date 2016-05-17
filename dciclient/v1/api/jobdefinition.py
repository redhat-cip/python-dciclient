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


RESOURCE = 'jobdefinitions'
TABLE_HEADERS = ['id', 'name', 'priority', 'active', 'comment',
                 'etag', 'created_at', 'updated_at']


def create(context, name, topic_id, priority=None, component_types=None):
    if component_types is None:
        component_types = []
    return base.create(context, RESOURCE, name=name, priority=priority,
                       topic_id=topic_id, component_types=component_types)


def list(context, topic_id, embed=None):
    return base.list(context, RESOURCE, topic_id=topic_id, embed=embed)


def get(context, id, where=None, embed=None):
    return base.get(context, RESOURCE, id=id, where=where, embed=embed)


def delete(context, id, etag):
    return base.delete(context, RESOURCE, id=id, etag=etag)


def annotate(context, id, comment, etag):
    return base.update(context, RESOURCE, id=id, etag=etag, comment=comment)


def setactive(context, id, active, etag):
    active_bool = active in ['True', 'true']
    return base.update(context, RESOURCE, id=id, etag=etag, active=active_bool)


def get_components(context, id):
    uri = '%s/%s/%s/components' % (context.dci_cs_api, RESOURCE, id)
    return context.session.get(uri)


def add_test(context, id, test_id):
    uri = '%s/%s/%s/tests' % (context.dci_cs_api, RESOURCE, id)
    return context.session.post(uri, json={'test_id': test_id})


def get_tests(context, id):
    uri = '%s/%s/%s/tests' % (context.dci_cs_api, RESOURCE, id)
    return context.session.get(uri)


def remove_test(context, id, test_id):
    uri = '%s/%s/%s/tests/%s' % (context.dci_cs_api, RESOURCE, id,
                                 test_id)
    return context.session.delete(uri)
