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


RESOURCE = 'files'
TABLE_HEADERS = ['id', 'name', 'content', 'mime', 'md5', 'jobstate_id',
                 'team_id', 'created_at']


def create(context, name, content, mime, jobstate_id, md5=None):
    return base.create(context, RESOURCE, name=name, content=content,
                       mime=mime, md5=md5, jobstate_id=jobstate_id)


def get(context, id, where=None, embed=None):
    return base.get(context, RESOURCE, id=id, where=where, embed=embed)


def list(context):
    return base.list(context, RESOURCE)


def update(context, name=None, content=None, mime=None, md5=None):
    return base.update(context, RESOURCE, name=name, content=content,
                       mime=mime, md5=md5)


def delete(context, id):
    return base.delete(context, RESOURCE, id=id)
