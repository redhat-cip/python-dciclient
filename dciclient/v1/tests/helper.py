# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Red Hat, Inc
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

from __future__ import unicode_literals
from dciclient.v1.api import jobdefinition
from dciclient.v1.api import team
from dciclient.v1.api import topic
from dciclient.v1.helper import create_jobdefinition_and_add_component


def test_create_jobdefinition_and_add_component(runner, dci_context,
                                                components, test_id, topic_id):
    create_jobdefinition_and_add_component(dci_context, components, test_id,
                                           topic_id, jobdef_name='Test suite')

    team_id = team.list(dci_context).json()['teams'][0]['id']
    topic.attach_team(dci_context, topic_id, team_id)
    jdefs = jobdefinition.list(dci_context, topic_id).json()['jobdefinitions']
    jdef_names = [jdef['name'] for jdef in jdefs]

    jd_id = [jdef['id'] for jdef in jdefs if jdef['name'] == 'Test suite'][0]

    assert 'Test suite' in jdef_names

    jdef_cmpt = jobdefinition.get_components(dci_context, jd_id).json()
    jdef_cmpt = jdef_cmpt['components']

    assert 'component1' == jdef_cmpt[0]['name']
    assert 'component2' == jdef_cmpt[1]['name']
