# -*- coding: utf-8 -*-
#
# Copyright (C) Red Hat, Inc
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

from dciclient.v1.api import identity


def test_my_team_id_as_regular_user(dci_context_user):
    team_id = identity.my_team_id(dci_context_user)
    assert team_id is not None


def test_my_team_id_as_remoteci(dci_context_remoteci):
    team_id = identity.my_team_id(dci_context_remoteci)
    assert team_id is not None
