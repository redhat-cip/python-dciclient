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

from dciclient.v1.handlers import component
from dciclient.v1.handlers import componenttype
from dciclient.v1.handlers import jobdefinition
from dciclient.v1.handlers import test


def test_add_component(http_session):
    l_componenttype = componenttype.ComponentType(http_session)
    l_component = component.Component(http_session)
    l_jobdefinition = jobdefinition.JobDefinition(http_session)
    l_test = test.Test(http_session)

    ct_id = l_componenttype.create(name='foo_ct') \
                           .json()['componenttype']['id']
    c_id = l_component.create(name='foo_c', componenttype_id=ct_id) \
                      .json()['component']['id']
    t_id = l_test.create(name='foo_t').json()['test']['id']
    jd_id = l_jobdefinition.create(name='foo_jd', test_id=t_id) \
                           .json()['jobdefinition']['id']

    l_jobdefinition.add_component(
        id=jd_id,
        component_id=c_id,
    )

    embed_c_id = l_jobdefinition.get(id=jd_id,
                                     embed=['jobdefinition_component']) \
                                .json()['jobdefinition']['jobdefinition_component']['component_id']

    assert c_id = embed_c_id
