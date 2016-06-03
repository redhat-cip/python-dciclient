# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Red Hat, Inc
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

from dciclient.v1.consumers import dciconsumer
from dciclient.v1.handlers import component
from dciclient.v1.handlers import jobdefinition
from dciclient.v1.handlers import test


class Feeder(dciconsumer.DCIConsumer):
    """A DCI feeder class"""

    def __init__(self, dci_cs_url, login, password):
        super(Feeder, self).__init__(dci_cs_url, login, password)
        self.component_ids = []

    def ensure_test(self, test_name):
        """Ensure test exist"""
        l_test = test.Test(self._s)
        return l_test.create(name=test_name).json()['test']['id']

    def create_component(self, component_data):
        """Create an entry in Component"""
        l_component = component.Component(self._s)

        result = l_component.create(**component_data).json()
        self.component_ids.append(result['component']['id'])

    def create_jobdefinition(self, name, test):
        """Create an entry in JobDefinition"""
        l_jobdefinition = jobdefinition.JobDefinition(self._s)

        jobdefinition_id = l_jobdefinition.create(
            name=name,
            test_id=test,
        ).json()['jobdefinition']['id']

        for component_id in self.component_ids:
            l_jobdefinition.add_component(
                id=jobdefinition_id,
                component_id=component_id,
            )
