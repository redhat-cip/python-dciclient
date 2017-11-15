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
import json

import os

try:
    from urlparse import parse_qsl
    from urlparse import urlparse
except ImportError:
    from urllib.parse import parse_qsl
    from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from requests.auth import AuthBase
from requests.packages.urllib3.util.retry import Retry

from dciauth import signature
from dciclient.v1.api import identity
from dciclient import version


class DciContextBase(object):
    API_VERSION = 'api/v1'

    def __init__(self, dci_cs_url, max_retries=0, user_agent=None):
        super(DciContextBase, self).__init__()
        self.session = self._build_http_session(user_agent, max_retries)
        self.dci_cs_api = '%s/%s' % (dci_cs_url, DciContext.API_VERSION)
        self.last_job_id = None

    @staticmethod
    def _build_http_session(user_agent, max_retries):
        session = requests.Session()
        session.headers.setdefault('Content-Type', 'application/json')
        if not user_agent:
            user_agent = 'python-dciclient_%s' % version.__version__
        session.headers['User-Agent'] = user_agent
        session.headers['Client-Version'] = (
            'python-dciclient_%s' % version.__version__
        )
        retries = Retry(total=max_retries,
                        backoff_factor=0.1)
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))

        return session

    def get_team_id(self):
        """Asks the control-server for the team_id of the currently
        authenticated resource.
        """
        return identity.get(self).json()['identity']['team_id']


class DciContext(DciContextBase):
    def __init__(self, dci_cs_url, login, password, max_retries=0,
                 user_agent=None):
        super(DciContext, self).__init__(dci_cs_url.rstrip('/'), max_retries,
                                         user_agent)
        self.login = login
        self.session.auth = (login, password)


def build_dci_context(dci_cs_url=None, dci_login=None, dci_password=None,
                      dci_api_secret=None, user_agent=None, max_retries=80):
    dci_cs_url = dci_cs_url or os.environ.get('DCI_CS_URL', '')
    dci_login = dci_login or os.environ.get('DCI_LOGIN', '')
    dci_password = dci_password or os.environ.get('DCI_PASSWORD', '')

    if not dci_cs_url or not dci_login or not dci_password:
        msg = "Environment variables required: DCI_CS_URL=%s, " \
              "DCI_LOGIN=%s, DCI_PASSWORD=%s" % \
              (dci_cs_url, dci_login, dci_password)
        raise Exception(msg)

    return DciContext(dci_cs_url.rstrip('/'), dci_login, dci_password,
                      user_agent=user_agent, max_retries=max_retries)


class DciHMACAuth(AuthBase):
    """Signs the request for DCI API with HMAC authentication"""

    def __init__(self, client_id, api_secret):
        self.client_id = self.get_backward_compatible_client_id(client_id)
        print('---------------')  # noqa
        print('- DciHMACAuth -')  # noqa
        print('---------------')  # noqa
        print('client_id', self.client_id)  # noqa
        self.api_secret = api_secret
        print('api_secret', self.api_secret)  # noqa

    @staticmethod
    def get_backward_compatible_client_id(client_id):
        if client_id.find('/') == -1:
            return 'remoteci/%s' % client_id
        return client_id

    def __call__(self, r):
        content_type = r.headers.get('Content-Type', '')
        url = urlparse(r.url)
        params = dict(parse_qsl(url.query))
        payload = self.get_payload(r)
        headers = signature.generate_headers_with_secret(
            secret=self.api_secret,
            method=r.method,
            content_type=content_type,
            url=url.path,
            params=params,
            payload=payload)
        headers['DCI-Client-Info'] = self.client_id
        r.headers.update(headers)
        print('content_type', content_type)  # noqa
        print('method', r.method)  # noqa
        print('url', url)  # noqa
        print('params', params)  # noqa
        print('payload', payload)  # noqa
        print('---------------')  # noqa
        return r

    def get_payload(self, r):
        try:
            return dict(json.loads(r.body or '{}'))
        except TypeError:
            return {}


class DciHMACContext(DciContextBase):
    def __init__(self, dci_cs_url, client_id, api_secret):
        super(DciHMACContext, self).__init__(dci_cs_url.rstrip('/'))
        self.session.auth = DciHMACAuth(client_id, api_secret)


class SsoContext(DciContextBase):
    def __init__(self, dci_cs_url, token, max_retries=0, user_agent=None):
        super(SsoContext, self).__init__(dci_cs_url.rstrip('/'), max_retries,
                                         user_agent)
        self.session.headers['Authorization'] = 'Bearer %s' % token


def build_sso_context(dci_cs_url, sso_url, username, password, token,
                      max_retries=0, user_agent=None, refresh=False):
    dci_cs_url = dci_cs_url or os.environ.get('DCI_CS_URL', '')
    sso_url = sso_url or os.environ.get('SSO_URL', '').rstrip('/')
    username = username or os.environ.get('SSO_USERNAME', '')
    password = password or os.environ.get('SSO_PASSWORD', '')
    token = token or os.environ.get('SSO_TOKEN', '')

    def _get_token():
        url = '%s/auth/realms/dci-test/protocol/openid-connect/token' % sso_url
        data = {'client_id': 'dci-cs',
                'grant_type': 'password',
                'username': username,
                'password': password}
        result = requests.Session().post(url, data=data)
        return result.json()['access_token']

    if not token or refresh:
        if not sso_url or not username or not password:
            msg = "Environment variables required to build token: SSO_URL, " \
                  "SSO_USERNAME, SSO_PASSWORD or use SSO_TOKEN."
            raise Exception(msg)
        token = _get_token()
    os.environ.set('SSO_TOKEN', token)

    return SsoContext(dci_cs_url, token, max_retries, user_agent)
