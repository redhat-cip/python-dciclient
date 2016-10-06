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
import os


RESOURCE = 'components'
TABLE_HEADERS = ['id', 'name', 'canonical_project_name',
                 'type', 'title', 'message', 'url',
                 'data', 'created_at', 'export_control',
                 'updated_at']
TABLE_FILE_HEADERS = ['id', 'name', 'mime', 'size', 'component_id',
                      'created_at']


GIT_COMMIT = 'git_commit'
KH_INSTALLER = 'kh_installer'
SNAPSHOT = 'snapshot'


def create(context, name, type, topic_id, canonical_project_name=None, data={},
           title=None, message=None, url=None, export_control=False):
    return base.create(context, RESOURCE, name=name, type=type,
                       canonical_project_name=canonical_project_name,
                       data=json.dumps(data), title=title, message=message,
                       url=url, topic_id=topic_id,
                       export_control=export_control)


def get(context, id, where=None, embed=None):
    return base.get(context, RESOURCE, id=id, where=where, embed=embed)


def update(context, id=None, etag=None, name=None, content=None):
    return base.update(context, RESOURCE, id=id, etag=etag, name=name,
                       content=content)


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
    r = context.session.get(uri, stream=True)
    with open(target + '.part', 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    os.rename(target + '.part', target)


def file_list(context, id):
    uri = '%s/%s/%s/files' % (context.dci_cs_api, RESOURCE, id)
    return context.session.get(uri)


def file_delete(context, id, file_id):
    uri = '%s/%s/%s/files/%s' % (context.dci_cs_api, RESOURCE, id, file_id)
    return context.session.delete(uri)
