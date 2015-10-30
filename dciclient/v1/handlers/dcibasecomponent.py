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

from dciclient.v1 import exceptions

import json


class DCIBaseComponent(object):

    def __init__(self, dci_client, endpoint_uri):
        self._dci_client = dci_client
        self._end_point_with_uri = '%s/%s' % (self._dci_client._end_point,
                                              endpoint_uri)

    def create(self, name):
        """Create a Component Type"""
        if not name:
            raise exceptions.ClientError('name parameter required.')

        return self._dci_client._s.post(self._end_point_with_uri,
                                        data=json.dumps({'name': name}))

    def list(self):
        """List all Components Type"""
        return self._dci_client._s.get(self._end_point_with_uri)

    def get(self, _id):
        """List a specific Components Type"""
        if not _id:
            raise exceptions.ClientError('componenttype id parameter required.')

        return self._dci_client._s.get("%s/%s" % (self._end_point_with_uri,
                                                  _id))

    def update(self, _id=None, etag=None, name=None):
        """Update a specific Components Type"""
        if not _id or not etag or not name:
            raise exceptions.ClientError("parameters missing: _id='%s', "
                              "etag='%s', name='%s'" %
                              (_id, etag, name))

        return self._dci_client._s.put("%s/%s" % (self._end_point_with_uri,
                                       _id), headers={'If-match': etag},
                                       data=json.dumps({'name': name}))

    def delete(self, _id, etag):
        if not _id or not etag:
            raise exceptions.ClientError("parameters missing: _id='%s', "
                              "etag='%s'" % (_id, etag))

        return self._dci_client._s.delete("%s/%s" % (self._end_point_with_uri,
                                          _id), headers={'If-match': etag})
