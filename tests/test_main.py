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

from dciclient.shell import main
from mock import patch
import sys


@patch("dciclient.shell.print_response")
@patch("dciclient.shell.run")
def test_build_valid_remoteci_context(
    mock_run, mock_printer, remoteci_id, remoteci_api_secret
):
    test_args = [
        "dcictl",
        "--dci-client-id",
        remoteci_id,
        "--dci-api-secret",
        remoteci_api_secret,
        "component-list",
        "--topic-id",
        "id",
    ]
    with patch.object(sys, "argv", test_args):
        main()
    assert mock_run.called
    assert mock_run.call_args_list[0][0][0] is not None
    assert mock_printer.called
