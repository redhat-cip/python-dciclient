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

from dciclient.v1.handlers.dcibasecomponent import DCIBaseComponent


class Test(DCIBaseComponent):
    ENDPOINT_URI = 'tests'

    def __init__(self, dci_client):
        DCIBaseComponent.__init__(self, dci_client, self.ENDPOINT_URI)

    def create(self, name):
        return super(Test, self).create()

    def list(self):
        return super(Test, self).list()

    def get(self, _id):
        return super(Test, self).get(_id)

    def update(self, _id=None, etag=None, name=None):
        return super(Test, self).update(_id, etag, name)

    def delete(self, _id, etag):
        return super(Test, self).delete(_id, etag)
