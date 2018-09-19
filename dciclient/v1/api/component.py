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


RESOURCE = 'components'


def create(context, name, type, topic_id, canonical_project_name=None, data={},
           title=None, message=None, url=None, export_control=True,
           state='active'):
    return base.create(context, RESOURCE, name=name, type=type,
                       canonical_project_name=canonical_project_name,
                       data=data, title=title, message=message,
                       url=url, topic_id=topic_id,
                       export_control=export_control, state=state)


def get(context, id, **kwargs):
    return base.get(context, RESOURCE, id=id, **kwargs)


def update(context, id=None, etag=None, name=None, content=None,
           export_control=None, state=None):
    return base.update(context, RESOURCE, id=id, etag=etag, name=name,
                       content=content, export_control=export_control,
                       state=state)


def delete(context, id):
    return base.delete(context, RESOURCE, id=id)


def file_upload(context, id, file_path):
    uri = '%s/%s/%s/files' % (context.dci_cs_api, RESOURCE, id)
    with open(file_path, 'rb') as f:
        return context.session.post(uri, data=f)


def file_get(context, id, file_id):
    uri = '%s/%s/%s/files/%s' % (context.dci_cs_api, RESOURCE, id, file_id)
    return context.session.get(uri)


def file_download(context, id, file_id, target):
    uri = '%s/%s/%s/files/%s/content' % (
        context.dci_cs_api, RESOURCE, id, file_id)
    return base.download(context, uri, target)


def file_list(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id, subresource='files', **kwargs)


def file_delete(context, id, file_id):
    return base.delete(context, RESOURCE, id,
                       subresource='files',
                       subresource_id=file_id)


def list_issues(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id,
                     subresource='issues', **kwargs)


def attach_issue(context, id, url):
    uri = '%s/%s/%s/issues' % (context.dci_cs_api, RESOURCE, id)
    data = {'url': url}
    return context.session.post(uri, json=data)


def unattach_issue(context, id, issue_id):
    return base.delete(context, RESOURCE, id,
                       subresource='issues',
                       subresource_id=issue_id)
