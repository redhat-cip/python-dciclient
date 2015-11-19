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

import json


class Test(dcibaseresource.DCIBaseResource):
    ENDPOINT_URI = 'tests'

    def __init__(self, session):
        super(Test, self).__init__(session, self.ENDPOINT_URI)

    def create(self, name, data=None):
        if data is None:
            data = '{}'

        return super(Test, self).create(name=name, data=json.loads(data))

    def update(self, id, etag, name, data=None):
        if data is None:
            return super(Test, self).update(id=id, etag=etag, name=name)
        else:
            return super(Test, self).update(id=id, etag=etag, name=name,
                                            data=json.loads(data))

    def delete(self, id, etag):
        return super(Test, self).delete(id=id, etag=etag)

    def show(self, id):
        return super(Test, self).show(id=id)
