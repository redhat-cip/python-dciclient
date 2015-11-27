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


class Test(dcibaseresource.DCIBaseResource):
    ENDPOINT_URI = 'tests'
    TABLE_HEADERS = ['id', 'name', 'data', 'etag', 'created_at', 'updated_at']

    def __init__(self, session):
        super(Test, self).__init__(session, self.ENDPOINT_URI)

    @property
    def table_headers(self):
        return self.TABLE_HEADERS

    @property
    def endpoint_uri(self):
        return self.ENDPOINT_URI

    def create(self, name, data=None):
        data = data or '{}'
        return super(Test, self).create(name=name, data=json.loads(data))

    def update(self, id, etag, name, data=None):
        kwargs = utils.sanitize_kwargs(id=id, etag=etag, name=name, data=data)
        return super(Test, self).update(**kwargs)

    def delete(self, id, etag):
        return super(Test, self).delete(id=id, etag=etag)

    def show(self, id):
        return super(Test, self).show(id=id)
