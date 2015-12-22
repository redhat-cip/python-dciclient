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

import os
import sys

import requests


class DciContext(object):
    API_VERSION = 'api/v1'

    def __init__(self, dci_cs_url, login, password):
        self.session = self._build_http_session(login, password)
        self.dci_cs_api = '%s/%s' % (dci_cs_url, DciContext.API_VERSION)

    @staticmethod
    def _build_http_session(login, password):
        session = requests.Session()
        session.headers.setdefault('Content-Type', 'application/json')
        session.auth = (login, password)
        return session


def build_dci_context(dci_cs_url=None, dci_login=None, dci_password=None):
    dci_cs_url = dci_cs_url or os.environ.get('DCI_CS_URL', '')
    dci_login = dci_login or os.environ.get('DCI_LOGIN', '')
    dci_password = dci_password or os.environ.get('DCI_PASSWORD', '')

    if not dci_cs_url or not dci_login or not dci_password:
        print("Environment variables required: DCI_CS_URL=%s, "
              "DCI_LOGIN=%s, DCI_PASSWORD=%s" %
              (dci_cs_url, dci_login, dci_password))
        sys.exit(1)
    return DciContext(dci_cs_url, dci_login, dci_password)


def create(context, resource, **kwargs):
    """Create a resource"""
    data = utils.sanitize_kwargs(**kwargs)
    uri = '%s/%s' % (context.dci_cs_api, resource)
    r = context.session.post(uri, json=data)
    r.raise_for_status()
    return r


def list(context, resource):
    """List all resources"""
    uri = '%s/%s' % (context.dci_cs_api, resource)
    r = context.session.get(uri)
    r.raise_for_status()
    return r


def get(context, resource, **kwargs):
    """List a specific resource"""
    uri = '%s/%s/%s' % (context.dci_cs_api, resource, kwargs.pop('id'))
    r = context.session.get(uri, params=kwargs)
    r.raise_for_status()
    return r


def update(context, resource, **kwargs):
    """Update a specific resource"""
    etag = kwargs.pop('etag')
    data = utils.sanitize_kwargs(**kwargs)
    uri = '%s/%s/%s' % (context.dci_cs_api, resource, kwargs.pop('id'))
    r = context.session.put(uri, headers={'If-match': etag}, json=data)
    r.raise_for_status()
    return r


def delete(context, resource, **kwargs):
    """Delete a specific resource"""
    etag = kwargs.pop('etag')
    uri = '%s/%s/%s' % (context.dci_cs_api, resource, kwargs.pop('id'))
    r = context.session.delete(uri, headers={'If-match': etag})
    r.raise_for_status()
    return r
