# -*- encoding: utf-8 -*-
#
# Copyright 2024 Red Hat, Inc.
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

import sys

import pytest
import responses

from dciclient.v1.api import context as dci_context


@responses.activate
def test_context_calls_once_on_status_ok():
    api_ctx = dci_context.DciContextBase(dci_cs_url="http://dciapi", max_retries=4)
    responses.add(method=responses.GET, url=api_ctx.dci_cs_api, status=200)

    r = api_ctx.session.get(api_ctx.dci_cs_api)
    assert r.status_code == 200
    assert responses.assert_call_count(api_ctx.dci_cs_api, 1)


@pytest.mark.xfail(
    sys.version_info < (3, 9), reason="This test is expected to fail before python 3.8"
)
@responses.activate
def test_context_retries_on_status_bad():
    api_ctx = dci_context.DciContextBase(dci_cs_url="http://dci/api/v1")
    responses.add(method=responses.GET, url="http://dci/api/v1", status=500)

    r = api_ctx.session.get("http://dci/api/v1")
    assert r.status_code == 500
    assert responses.assert_call_count("http://dci/api/v1", 11)
