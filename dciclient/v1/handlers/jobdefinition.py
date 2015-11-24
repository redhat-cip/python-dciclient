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


class JobDefinition(dcibaseresource.DCIBaseResource):
    ENDPOINT_URI = 'jobdefinitions'

    def __init__(self, session):
        super(JobDefinition, self).__init__(session, self.ENDPOINT_URI)

    def create(self, name, test_id, priority):
        return super(JobDefinition, self).create(name=name, test_id=test_id,
                                                 priority=priority)

    def update(self, id, etag, name, test_id=None, priority=None):
        kwargs = utils.sanitize_kwargs(id=id, etag=etag, name=name,
                                       test_id=test_id, priority=priority)
        return super(JobDefinition, self).update(**kwargs)

    def delete(self, id, etag):
        return super(JobDefinition, self).delete(id=id, etag=etag)

    def show(self, id):
        return super(JobDefinition, self).show(id=id)
