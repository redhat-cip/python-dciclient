# -*- encoding: utf-8 -*-
#
# Copyright Red Hat, Inc.
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


RESOURCE = 'jobs_events'


def list(context, sequence, limit=10, offset=0):
    params = {'limit': limit,
              'offset': offset}
    uri = '%s/%s/%s' % (context.dci_cs_api, RESOURCE, sequence)
    return context.session.get(uri, params=params)


def iter(context, sequence, limit=10):
    """Iter to list all the jobs events."""
    params = {'limit': limit,
              'offset': 0}
    uri = '%s/%s/%s' % (context.dci_cs_api, RESOURCE, sequence)

    while True:
        j = context.session.get(uri, params=params).json()
        if len(j['jobs_events']):
            for i in j['jobs_events']:
                yield i
        else:
            break
        params['offset'] += params['limit']


def delete(context, sequence):
    """Delete jobs events from a given sequence"""
    uri = '%s/%s/%s' % (context.dci_cs_api, RESOURCE, sequence)
    return context.session.delete(uri)


def get_sequence(context):
    uri = '%s/%s/sequence' % (context.dci_cs_api, RESOURCE)
    return context.session.get(uri)


def update_sequence(context, etag, sequence):
    uri = '%s/%s/sequence' % (context.dci_cs_api, RESOURCE)
    return context.session.put(uri, timeout=base.HTTP_TIMEOUT,
                               headers={'If-match': etag},
                               json={'sequence': sequence})
