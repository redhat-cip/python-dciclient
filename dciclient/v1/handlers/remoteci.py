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

from dciclient.v1.handlers import dcibaseresource
from dciclient.v1 import utils

import json


class RemoteCI(dcibaseresource.DCIBaseResource):
    ENDPOINT_URI = 'remotecis'
    TABLE_HEADERS = ['id', 'name', 'data', 'team_id', 'etag', 'created_at',
                     'updated_at']

    def __init__(self, session):
        super(RemoteCI, self).__init__(session, self.ENDPOINT_URI)

    def create(self, name, team_id, data=None):
        data = data or '{}'
        return super(RemoteCI, self).create(name=name, team_id=team_id,
                                            data=json.loads(data))

    def update(self, id, etag, name, team_id=None, data=None):
        kwargs = utils.sanitize_kwargs(id=id, etag=etag, name=name,
                                       team_id=team_id, data=data)
        return super(RemoteCI, self).update(**kwargs)

    def delete(self, id, etag):
        return super(RemoteCI, self).delete(id=id, etag=etag)

    def get(self, id, where=None, embed=None):
        return super(RemoteCI, self).get(id=id, where=where, embed=embed)
