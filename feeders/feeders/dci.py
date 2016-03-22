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

from dciclient.v1.api import component
from dciclient.v1.api import context
from dciclient.v1 import helper

import click
import requests

CANDIDATES_URL = 'http://dci.enovance.com/candidates/'


def get_components(dci_context, url, topic_id):
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


@click.command()
@click.option('--dci-login', envvar='DCI_LOGIN', required=True,
              help="DCI username account.")
@click.option('--dci-password', envvar='DCI_PASSWORD', required=True,
              help="DCI password account.")
@click.option('--dci-cs-url', envvar='DCI_CS_URL', required=True,
              help="DCI CS url.")
@click.option('--dci-topic-id', envvar='DCI_TOPIC_ID', required=True,
              help="DCI topic id.")
def main(dci_login, dci_password, dci_cs_url, dci_topic_id):

    dci_context = context.build_dci_context(dci_cs_url, dci_login,
                                            dci_password)

    components = get_components(dci_context, CANDIDATES_URL, dci_topic_id)
    test_id = helper.get_test_id(dci_context, 'scenario01', dci_topic_id)

    helper.create_jobdefinition_and_add_component(dci_context, components,
                                                  test_id, dci_topic_id)


if __name__ == '__main__':
    main()
