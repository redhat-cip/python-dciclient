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

import json

RESOURCE = 'components'
TABLE_HEADERS = ['id', 'name', 'canonical_project_name',
                 'type', 'sha', 'title', 'message', 'url',
                 'git', 'ref', 'data', 'etag', 'created_at', 'updated_at']

GIT_COMMIT = 'git_commit'
KH_INSTALLER = 'kh_installer'
PUDDLE = 'puddle'


def create(context, name, type, canonical_project_name=None, data={}, sha=None,
           title=None, message=None, url=None, git=None, ref=None):
    return base.create(context, RESOURCE, name=name, type=type,
                       canonical_project_name=canonical_project_name,
                       data=json.dumps(data), sha=sha, title=title,
                       message=message, url=url, git=git, ref=ref)


def list(context):
    return base.list(context, RESOURCE)


def get(context, id, where=None, embed=None):
    return base.get(context, RESOURCE, id=id, where=where, embed=embed)


def delete(context, id, etag):
    return base.delete(context, RESOURCE, id=id, etag=etag)
