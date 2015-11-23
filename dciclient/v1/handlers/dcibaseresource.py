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


class DCIBaseResource(object):
    API_URI = 'api/v1'

    def __init__(self, session, endpoint_uri):
        self._s = session
        self._end_point_with_uri = '%s/%s/%s' % (self._s.dci_cs_url,
                                                 self.API_URI, endpoint_uri)

    def create(self, **kwargs):
        """Create a resource"""
        return self._s.post(self._end_point_with_uri, json=kwargs)

    def list(self):
        """List all resources"""
        return self._s.get(self._end_point_with_uri)

    def get(self, **kwargs):
        """List a specific resource"""
        return self._s.get("%s/%s" % (self._end_point_with_uri, kwargs['id']))

    def update(self, **kwargs):
        """Update a specific resource"""
        # NOTE(spredzy): Extract the data from the kwargs. Are considered data
        # any dictionnary member that is not id or etag.
        data_keys = list(set(kwargs.keys()) - set(['id', 'etag']))
        data = dict(filter(lambda i: i[0] in data_keys, kwargs.iteritems()))

        return self._s.put('%s/%s' % (self._end_point_with_uri, kwargs['id']),
                           headers={'If-match': kwargs['etag']}, json=data)

    def delete(self, **kwargs):
        """Delete a specific resource"""
        return self._s.delete('%s/%s' % (self._end_point_with_uri,
                                         kwargs['id']),
                              headers={'If-match': kwargs['etag']})
