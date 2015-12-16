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

from dciclient.v1 import utils


class DCIBaseResource(object):
    API_URI = 'api/v1'

    def __init__(self, session, endpoint_uri):
        self._s = session
        self._end_point_with_uri = '%s/%s/%s' % (self._s.dci_cs_url,
                                                 self.API_URI, endpoint_uri)

    def create(self, **kwargs):
        """Create a resource"""
        data = utils.sanitize_kwargs(**kwargs)
        r = self._s.post(self._end_point_with_uri, json=data)
        r.raise_for_status()
        return r

    def list(self):
        """List all resources"""
        r = self._s.get(self._end_point_with_uri)
        r.raise_for_status()
        return r

    def get(self, **kwargs):
        """List a specific resource"""
        base_url = "%s/%s" % (self._end_point_with_uri, kwargs.pop('id'))
        r = self._s.get(base_url, params=kwargs)
        r.raise_for_status()
        return r

    def update(self, **kwargs):
        """Update a specific resource"""
        id = kwargs.pop('id')
        etag = kwargs.pop('etag')
        data = utils.sanitize_kwargs(**kwargs)
        r = self._s.put('%s/%s' % (self._end_point_with_uri, id),
                        headers={'If-match': etag}, json=data)
        r.raise_for_status()
        return r

    def delete(self, **kwargs):
        """Delete a specific resource"""
        r = self._s.delete('%s/%s' % (self._end_point_with_uri,
                                      kwargs['id']),
                           headers={'If-match': kwargs['etag']})
        r.raise_for_status()
        return r
