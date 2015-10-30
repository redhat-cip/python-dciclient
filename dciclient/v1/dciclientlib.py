# -*- encoding: utf-8 -*-
#
# Copyright 2015 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import unicode_literals

import json
import requests


class DCIClient(object):

    def __init__(self, end_point, login, password):
        if not end_point or not login or not password:
            raise ClientError("Missing parameters: end_point='%s', "
                              "login='%s', password='%s'" % (end_point,
                                                             login, password))
        self._end_point = end_point
        # init session with credentials
        self._s = requests.Session()
        self._s.headers.setdefault('Content-Type', 'application/json')
        self._s.auth = (login, password)

    @staticmethod
    def _return_result(result, expected_status_code):
        if result.status_code != expected_status_code:
            raise ServerError(result.text)
        return result

    def create_componenttype(self, name):
        if not name:
            raise ClientError('name parameter required.')

        r = self._s.post("%s/componenttypes" % self._end_point,
                         data=json.dumps({'name': name}))
        return self._return_result(r, 201)

    def get_all_componenttypes(self):
        r = self._s.get("%s/componenttypes" % self._end_point)
        return self._return_result(r, 200)

    def get_componenttype(self, componenttype_id):
        if not componenttype_id:
            raise ClientError('componenttype id parameter required.')

        r = self._s.get("%s/componenttypes/%s" % (self._end_point,
                                                  componenttype_id))
        return self._return_result(r, 200)

    def put_componenttype(self, componenttype_id, etag, name):
        if not componenttype_id or not etag:
            raise ClientError("parameters missing: componenttype_id='%s', "
                              "etag='%s'" % (componenttype_id, etag))

        r = self._s.put("%s/componenttypes/%s" %
                        (self._end_point, componenttype_id),
                        headers={'If-match': etag},
                        data=json.dumps({'name': name}))
        return self._return_result(r, 204)

    def delete_componenttype(self, componenttype_id, etag):
        if not componenttype_id or not etag:
            raise ClientError("parameters missing: componenttype_id='%s', "
                              "etag='%s'" % (componenttype_id, etag))

        r = self._s.delete("%s/componenttypes/%s" %
                           (self._end_point, componenttype_id),
                           headers={'If-match': etag})
        return self._return_result(r, 204)


class ClientError(Exception):
    """DCI client error."""


class ServerError(Exception):
    """DCI Control Server error."""
