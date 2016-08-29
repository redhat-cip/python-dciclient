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


RESOURCE = 'tests'
TABLE_HEADERS = ['id', 'name', 'data', 'created_at']


def create(context, name, team_id, data={}):
    return base.create(context, RESOURCE, name=name, data=data,
                       team_id=team_id)


def list(context, team_id):
    return base.list(context, RESOURCE, team_id=team_id)


def get(context, id, where=None, embed=None):
    return base.get(context, RESOURCE, id=id, where=where, embed=embed)


def delete(context, id):
    return base.delete(context, RESOURCE, id=id)
