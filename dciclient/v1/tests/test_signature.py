# -*- encoding: utf-8 -*-
#
# Copyright 2015-2016 Red Hat, Inc.
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

from datetime import datetime
import requests

from dciclient.v1.api import job
from dciclient.v1 import auth
import dciclient.v1.tests.shell_commands.utils as utils


def make_blank_session(server):
    s = requests.Session()
    flask_adapter = utils.FlaskHTTPAdapter(server.test_client())
    s.mount('http://dciserver.com', flask_adapter)
    return s


def test_get_job_with_no_auth_fails(server, job_id):
    s = make_blank_session(server)
    r = s.get('http://dciserver.com/api/v1/jobs/%s' % job_id)
    assert r.status_code == 401


def test_get_job_with_signature_succeeds(server, job_id, remoteci_id,
                                         remoteci_api_secret):
    timestamp = datetime.utcnow()
    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%SZ')
    signature = auth.sign(
        secret=remoteci_api_secret, http_verb='GET',
        content_type='application/json',
        timestamp=datetime.utcnow(),
        url='/api/v1/jobs/%s' % job_id,
        query_string='',
        payload=''
    )

    sig_headers = {
        'DCI-Client-Info': '%s/remoteci/%s' % (timestamp_str, remoteci_id),
        'DCI-Auth-Signature': signature,
        'Content-Type': 'application/json',
    }

    s = make_blank_session(server)
    r = s.get('http://dciserver.com/api/v1/jobs/%s' % job_id,
              headers=sig_headers)
    assert r.status_code == 200


def test_get_job_with_remoteci_context_succeeds(dci_context_remoteci,
                                                job_id):
    r = job.get(dci_context_remoteci, job_id)
    assert r.status_code == 200
