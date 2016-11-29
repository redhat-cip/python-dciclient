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
from requests.auth import AuthBase
from requests.compat import urlparse
from requests.packages.urllib3.util.retry import Retry

from dciclient.v1 import token
from dciclient import version


class DciContextBase(object):
    API_VERSION = 'api/v1'

    def __init__(self, dci_cs_url, max_retries=0, user_agent=None):
        super(DciContextBase, self).__init__()
        retries = Retry(total=max_retries,
                        backoff_factor=0.1)
        self._build_http_session(user_agent)
        retries = Retry(total=max_retries,
                        backoff_factor=0.1)
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.dci_cs_api = '%s/%s' % (dci_cs_url, DciContext.API_VERSION)
        self.last_jobstate_id = None
        self.last_job_id = None

    def _build_http_session(self, user_agent):
        self.session = requests.Session()
        self.session.headers.setdefault('Content-Type', 'application/json')
        if not user_agent:
            self.user_agent = 'python-dciclient_%s' % version.__version__
        self.session.headers['User-Agent'] = user_agent
        self.session.headers['Client-Version'] = (
            'python-dciclient_%s' % version.__version__
        )


class DciContext(DciContextBase):
    def __init__(self, dci_cs_url, login, password, max_retries=0,
                 user_agent=None):
        super(DciContext, self).__init__(dci_cs_url, max_retries, user_agent)
        self.login = login
        self.session.auth = (login, password)


class DciCiApiAuth(AuthBase):
    """Signs the request for DCI API secret authentication"""
    def __init__(self, remoteci, api_secret):
        self.remoteci = remoteci
        self.api_secret = api_secret

    def __call__(self, r):
        content_type = r.headers.get('Content-Type', '')
        url_p = urlparse(r.url)
        signature = token.gen_header(self.remoteci, self.api_secret,
                                     r.method, content_type, url_p.path,
                                     url_p.query, r.body)
        r.headers.update(signature)
        r.prepare_headers(r.headers)

        return r


class DciRemoteCiContext(DciContextBase):
    def __init__(self, dci_cs_url, remoteci, api_secret, max_retries=0,
                 user_agent=None):
        super(DciRemoteCiContext, self).__init__(dci_cs_url, max_retries,
                                                 user_agent)
        self.session.auth = DciCiApiAuth(remoteci, api_secret)


def build_dci_context(dci_cs_url=None, dci_login=None, dci_password=None,
                      dci_api_secret=None, user_agent=None, max_retries=80):
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


def build_remoteci_context(dci_cs_url=None, dci_remoteci=None,
                           dci_api_secret=None, user_agent=None,
                           max_retries=80):
    dci_cs_url = dci_cs_url or os.environ.get('DCI_CS_URL', '')
    dci_remoteci = dci_remoteci or os.environ.get('DCI_REMOTECI', '')
    dci_api_secret = dci_api_secret or os.environ.get('DCI_API_SECRET', '')

    if not dci_cs_url or not dci_remoteci or not dci_api_secret:
        print("Environment variables required: DCI_CS_URL=%s, "
              "DCI_REMOTECI=%s, DCI_API_SECRET=%s" %
              (dci_cs_url, dci_remoteci, dci_api_secret))
        sys.exit(1)
    return DciRemoteCiContext(dci_cs_url, dci_remoteci, dci_api_secret,
                              user_agent=user_agent, max_retries=max_retries)
