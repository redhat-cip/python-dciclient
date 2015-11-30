# -*- encoding: utf-8 -*-
#
# Copyright 2015 Red Hat, Inc.
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

from dciclient.v1.handlers import remoteci
from dciclient.v1.handlers import team


def test_embed(http_session):
    l_team = team.Team(http_session)
    l_remoteci = remoteci.RemoteCI(http_session)

    team_id = l_team.create(name='teama').json()['team']['id']
    remoteci_id = l_remoteci.create(name='boa', team_id=team_id) \
                            .json()['remoteci']['id']

    embed_team_id = l_remoteci.get(id=remoteci_id, embed=['team']) \
                              .json()['remoteci']['team']['id']

    assert team_id == embed_team_id
