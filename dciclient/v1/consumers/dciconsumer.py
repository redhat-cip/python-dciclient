# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import requests


class DCIConsumer(object):
    """A DCI consumer base class"""

    def __init__(self, dci_cs_url, login, password):
        self._s = self._get_http_session(dci_cs_url, login, password)

    def _get_http_session(self, dci_cs_url, login, password):
        session = requests.Session()
        session.headers.setdefault('Content-Type', 'application/json')
        session.auth = (login, password)
        session.dci_cs_url = dci_cs_url
        return session
