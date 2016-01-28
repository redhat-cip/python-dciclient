#!/usr/bin/env python
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

from dciclient.v1.api import component
from dciclient.v1.api import context
from dciclient.v1.api import jobdefinition
from dciclient.v1.api import test


def get_dummy_component():
    """Retrieve a dummy component"""

    dummy_component = {
        "type": component.GIT_COMMIT,
        "name": 'a dummy component',
        "canonical_project_name": 'dummy'
    }

    return dummy_component


def get_test_id(dci_context, name):
    print("Use test '%s'" % name)
    test.create(dci_context, name)
    return test.get(dci_context, name).json()['test']['id']


if __name__ == '__main__':
    dci_context = context.build_dci_context()
    # Create Khaleesi-tempest test
    dummy_test_id = get_test_id(dci_context, 'dummy')

    components = [get_dummy_component()]

    # If at least one component doesn't exist in the database then a new
    # jobdefinition must be created.
    at_least_one = False
    component_ids = []
    for cmpt in components:
        created_cmpt = component.create(dci_context, **cmpt)
        if created_cmpt.status_code == 201:
            print("Create component '%s', type '%s'" % (cmpt['name'],
                                                        cmpt['type']))
            component_ids.append(created_cmpt.json()['component']['id'])
            at_least_one = True

    if at_least_one:
        jobdef_name = 'Dummy'
        jobdef = jobdefinition.create(dci_context, jobdef_name,
                                      dummy_test_id)
        if jobdef.status_code == 201:
            jobdef_id = jobdef.json()['jobdefinition']['id']
            for cmpt_id in component_ids:
                jobdefinition.add_component(dci_context, jobdef_id, cmpt_id)
            print("Jobdefinition '%s' created." % jobdef_name)
        else:
            print("Error on jobdefinition creation: '%s'", jobdef.json())
    else:
        print("No jobdefinition created.")
