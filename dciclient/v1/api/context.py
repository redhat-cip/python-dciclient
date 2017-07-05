# Copyright 2015-2016 Red Hat, Inc.
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

import os
import sys

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from dciclient import version


class DciContext(object):
    API_VERSION = 'api/v1'

    def __init__(self, dci_cs_url, login, password, max_retries=0,
                 user_agent=None):
        self.session = self._build_http_session(login, password, user_agent)
        retries = Retry(total=max_retries,
                        backoff_factor=0.1)
        self.login = login
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.dci_cs_api = '%s/%s' % (dci_cs_url, DciContext.API_VERSION)
        self.last_jobstate_id = None
        self.last_job_id = None

    @staticmethod
    def _build_http_session(login, password, user_agent):
        session = requests.Session()
        session.headers.setdefault('Content-Type', 'application/json')
        if not user_agent:
            user_agent = 'python-dciclient_%s' % version.__version__
        session.headers['User-Agent'] = user_agent
        session.headers['Client-Version'] = (
            'python-dciclient_%s' % version.__version__
        )
        session.auth = (login, password)
        return session


def build_dci_context(dci_cs_url=None, dci_login=None, dci_password=None,
                      user_agent=None, max_retries=80):
    dci_cs_url = dci_cs_url or os.environ.get('DCI_CS_URL', '')
    dci_login = dci_login or os.environ.get('DCI_LOGIN', '')
    dci_password = dci_password or os.environ.get('DCI_PASSWORD', '')

    if not dci_cs_url or not dci_login or not dci_password:
        print("Environment variables required: DCI_CS_URL=%s, "
              "DCI_LOGIN=%s, DCI_PASSWORD=%s" %
              (dci_cs_url, dci_login, dci_password))
        sys.exit(1)
    return DciContext(dci_cs_url, dci_login, dci_password,
                      user_agent=user_agent, max_retries=max_retries)
