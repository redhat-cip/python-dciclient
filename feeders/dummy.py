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

from optparse import OptionParser

import random

ID = random.randint(1, 99999)


def get_dummy_component():
    """Retrieve a dummy component"""

    dummy_component = {
        "type": component.GIT_COMMIT,
        "name": 'a dummy component %s' % ID,
        "canonical_project_name": 'dummy %s' % ID
    }

    return dummy_component


def get_test_id(dci_context, name):
    print("Use test '%s'" % name)
    test.create(dci_context, name)
    return test.get(dci_context, name).json()['test']['id']


def parse_command_line():
    parser = OptionParser("")
    parser.add_option("-u", "--dci-login", dest="dci_login",
                      help="DCI login")
    parser.add_option("-p", "--dci-password", dest="dci_password",
                      help="DCI password")
    parser.add_option("-a", "--dci-cs-url", dest="dci_cs_url",
                      help="DCI CS url")

    return parser.parse_args()


def main():
    (options, args) = parse_command_line()

    dci_context = context.build_dci_context(options.dci_cs_url,
                                            options.dci_login,
                                            options.dci_password)
    # Create a dummy test
    dummy_test_id = get_test_id(dci_context, 'dummy %s' % ID)

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
        jobdef_name = 'Dummy %s' % ID
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

if __name__ == '__main__':
    main()
