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

from dciclient.v1.api import job
from dciclient import version

import mock


def test_standard_headers(job_id, dci_context):
    with mock.patch('requests.sessions.Session.send'):
        job.get(dci_context, job_id)
        # the request that will be should be send
        prepared_request = dci_context.session.send.call_args[0]
        ua = 'python-dciclient_' + version.__version__
        assert prepared_request[0].headers['User-Agent'] == ua
        assert prepared_request[0].headers['Client-Version'] == (
            'python-dciclient_%s' % version.__version__
        )


def test_ua_headers(job_id, dci_context_other_user_agent):
    with mock.patch('requests.sessions.Session.send'):
        job.get(dci_context_other_user_agent, job_id)
        # the request that will be should be send
        prepared_request = (dci_context_other_user_agent.session.send
                            .call_args[0])
        assert prepared_request[0].headers['User-Agent'] == 'myagent-0.1'
        assert prepared_request[0].headers['Client-Version'] == (
            'python-dciclient_%s' % version.__version__
        )
