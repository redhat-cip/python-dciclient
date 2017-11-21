# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Red Hat, Inc
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

from dciclient.v1.api import component


def test_success_download_component_file_returns_http_response(dci_context,
                                                               component_id,
                                                               tmpdir):
    """Ensure an http response is retrieved."""

    tmp_file = tmpdir.mkdir('data').join('content')
    tmp_file.write('DISTRIBUTED-CI')

    component.file_upload(dci_context, component_id, tmp_file.strpath)

    file_id = component.file_list(
        dci_context, component_id
    ).json()['component_files'][0]['id']

    res = component.file_download(dci_context, component_id, file_id,
                                  tmp_file.strpath)

    assert res.status_code == 200
