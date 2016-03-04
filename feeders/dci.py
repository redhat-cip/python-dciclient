#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2016 Red Hat, Inc.
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

from dciclient.v1 import helper
from dciclient.v1.api import component
from dciclient.v1.api import context
from dciclient.v1.api import test

from optparse import OptionParser

import requests
import sys

CANDIDATES_URL = 'http://dci.enovance.com/candidates/'


def get_dci_candidate_component(dci_context, url, topic_id):
    """Add the missing candidates in the components database"""
    rcs = []
    dci_candidate_components = []

    candidates = requests.get('%s/index.json' % url).json().keys()
    candidates.pop()  # Remove the 'latest' component that is a link

    registered_components = component.list(dci_context,
                                           topic_id).json()['components']

    for registered_component in registered_components:
        if registered_component['canonical_project_name'] == 'dci-candidate':
            rcs.append(registered_component['name'].replace(
                'dci-candidate ',
                '')
            )

    non_registered_candidates = list(set(candidates) - set(rcs))

    for candidate in non_registered_candidates:
        dci_candidate_components.append({
            'type': component.SNAPSHOT,
            'canonical_project_name': 'dci-candidate',
            'name': 'dci-candidate %s' % candidate,
            'url': '%s/%s' % (url, candidate),
            'topic_id': topic_id
        })

    return dci_candidate_components


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

    try:
        topic_id = args
    except ValueError:
        print('dci-feeder-dci topic_id')
        sys.exit(1)

    components = get_dci_candidate_component(
        dci_context,
        CANDIDATES_URL,
        topic_id
    )
    test_id = helper.get_test_id(dci_context, 'scenario01', topic_id)

    helper.create_jobdefinition_and_add_component(dci_context,
                                                  components,
                                                  test_id)


if __name__ == '__main__':
    main()
