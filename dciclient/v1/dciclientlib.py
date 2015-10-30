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

from dciclient.v1 import exceptions

import requests


class DCIClient(object):

    def __init__(self, end_point, login, password):
        if not end_point or not login or not password:
            raise exceptions.ClientError("Parameters missing: ensure "
                                         "dci-login, dci-password and "
                                         "dci-cs-url are set")
        self._end_point = end_point
        # init session with credentials
        self._s = requests.Session()
        self._s.headers.setdefault('Content-Type', 'application/json')
        self._s.auth = (login, password)
