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


RESOURCE = 'users'
TABLE_HEADERS = ['id', 'etag', 'name', 'role', 'team_id',
                 'created_at', 'updated_at']


def create(context, name, password, team_id, role=None):
    return base.create(context, RESOURCE, name=name, password=password,
                       role=role, team_id=team_id)


def list(context, where=None, embed=None):
    return base.list(context, RESOURCE, where=where, embed=embed)


def get(context, id, where=None, embed=None):
    return base.get(context, RESOURCE, id=id, where=where, embed=embed)


def update(context, id, etag, name, password, role):
    return base.update(context, RESOURCE, id=id, etag=etag, name=name,
                       password=password, role=role)


def delete(context, id, etag):
    return base.delete(context, RESOURCE, id=id, etag=etag)
