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


RESOURCE = 'files_events'


def list(context, sequence, limit=10, offset=0):
    params = {'limit': limit,
              'offset': offset}
    uri = '%s/%s/%s' % (context.dci_cs_api, RESOURCE, sequence)
    return context.session.get(uri, params=params)


def iter(context, sequence, limit=10):
    """Iter to list all the files events."""
    params = {'limit': limit,
              'offset': 0}
    uri = '%s/%s/%s' % (context.dci_cs_api, RESOURCE, sequence)

    while True:
        j = context.session.get(uri, params=params).json()
        if len(j['files']):
            for i in j['files']:
                yield i
        else:
            break
        params['offset'] += params['limit']
