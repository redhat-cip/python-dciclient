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

from dciclient.v1 import utils


def create(context, resource, **kwargs):
    """Create a resource"""
    data = utils.sanitize_kwargs(**kwargs)
    uri = '%s/%s' % (context.dci_cs_api, resource)
    r = context.session.post(uri, json=data)
    return r


def list(context, resource):
    """List all resources"""
    uri = '%s/%s' % (context.dci_cs_api, resource)
    r = context.session.get(uri)
    return r


def get(context, resource, **kwargs):
    """List a specific resource"""
    uri = '%s/%s/%s' % (context.dci_cs_api, resource, kwargs.pop('id'))
    r = context.session.get(uri, params=kwargs)
    return r


def update(context, resource, **kwargs):
    """Update a specific resource"""
    etag = kwargs.pop('etag')
    id = kwargs.pop('id')
    data = utils.sanitize_kwargs(**kwargs)
    uri = '%s/%s/%s' % (context.dci_cs_api, resource, id)
    r = context.session.put(uri, headers={'If-match': etag}, json=data)
    return r


def delete(context, resource, **kwargs):
    """Delete a specific resource"""

    etag = None
    if 'etag' in kwargs:
        etag = kwargs.pop('etag')
    uri = '%s/%s/%s' % (context.dci_cs_api, resource, kwargs.pop('id'))
    r = context.session.delete(uri, headers={'If-match': etag})
    return r
