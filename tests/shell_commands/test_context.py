# -*- encoding: utf-8 -*-
#
# Copyright Red Hat, Inc.
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

from mock import patch
from dciclient.v1.shell_commands.cli import parse_arguments
from dciclient.v1.shell_commands.context import get_context


def test_get_context():
    args = parse_arguments(
        ["user-list"],
        {
            "DCI_CLIENT_ID": "remoteci/3be167c8-488a-b3ae-acbc-d4d70010e71a",
            "DCI_API_SECRET": "Lwy0tYqGDkSV985xs9O9S2pJaIIT2DvH7bfJ7v1LBYBUSvTFx3sXGsV4vUCkDJkI",
            "DCI_CS_URL": "https://api.distributed-ci.io/",
        },
    )
    context = get_context(args)
    assert context.session.auth.client_type == "remoteci"
    assert context.session.auth.client_id == "3be167c8-488a-b3ae-acbc-d4d70010e71a"
    assert (
        context.session.auth.api_secret
        == "Lwy0tYqGDkSV985xs9O9S2pJaIIT2DvH7bfJ7v1LBYBUSvTFx3sXGsV4vUCkDJkI"
    )
