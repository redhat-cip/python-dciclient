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


RESOURCE = 'jobdefinitions'
TABLE_HEADERS = ['id', 'name', 'priority', 'test_id', 'etag', 'created_at',
                 'updated_at']


def create(context, name, topic_id, test_id=None, priority=None):
    return base.create(context, RESOURCE, name=name, test_id=test_id,
                       priority=priority, topic_id=topic_id)


def list(context, topic_id):
    return base.list(context, RESOURCE, topic_id=topic_id)


def get(context, id, where=None, embed=None):
    return base.get(context, RESOURCE, id=id, where=where, embed=embed)


def delete(context, id, etag):
    return base.delete(context, RESOURCE, id=id, etag=etag)


def add_component(context, id, component_id):
    uri = '%s/%s/%s/components' % (context.dci_cs_api, RESOURCE, id)
    return context.session.post(uri, json={'component_id': component_id})


def get_components(context, id):
    uri = '%s/%s/%s/components' % (context.dci_cs_api, RESOURCE, id)
    return context.session.get(uri)


def remove_component(context, id, component_id):
    uri = '%s/%s/%s/components/%s' % (context.dci_cs_api, RESOURCE, id,
                                      component_id)
    return context.session.delete(uri)
