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

from dciclient.v1 import utils

from dciclient.v1.api import base


RESOURCE = 'analytics'


def create(context, job_id, name, type, url, data):
    data = utils.sanitize_kwargs(name=name, type=type, url=url, data=data)
    uri = '%s/jobs/%s/%s' % (context.dci_cs_api, job_id, RESOURCE)
    return context.session.post(uri, timeout=base.HTTP_TIMEOUT, json=data)


def get(context, id, job_id):
    uri = '%s/jobs/%s/%s/%s' % (context.dci_cs_api, job_id, RESOURCE, id)
    return context.session.get(uri, timeout=base.HTTP_TIMEOUT)


def list(context, job_id):
    uri = '%s/jobs/%s/%s' % (context.dci_cs_api, job_id, RESOURCE)
    return context.session.get(uri, timeout=base.HTTP_TIMEOUT)


def put(context, id, job_id, etag, name, type, url, data):
    put_data = utils.sanitize_kwargs(name=name, type=type, url=url, data=data)
    uri = '%s/jobs/%s/%s/%s' % (context.dci_cs_api, job_id, RESOURCE, id)
    return context.session.put(uri, timeout=base.HTTP_TIMEOUT, json=put_data,
                               headers={'If-match': etag})


def delete(context, id, job_id):
    uri = '%s/jobs/%s/%s/%s' % (context.dci_cs_api, job_id, RESOURCE, id)
    return context.session.delete(uri, timeout=base.HTTP_TIMEOUT)
