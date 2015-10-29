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

# This script will connect on a Gerrit server and list the pending reviews.
# It will create the associated review in the DCI server and associate the
# tox check.
# If the version already exist, it will sync back the status of the version
# in Gerrit (-1/0/+1)

import argparse
import os
import sys

import yaml

from agents.utils import gerritlib
from dciclient import v1 as client_v1

def init_conf():
    parser = argparse.ArgumentParser(description='Gerrit agent.')
    parser.add_argument("--config-file", action="store",
                        help="the configuration file path")
    conf = parser.parse_args()
    return yaml.load(open(conf.config_file).read())


def main():
    config_file = init_conf()

    dci_client = client_v1.DCIClient()
    gerrit = gerritlib.Gerrit(
        config_file['gerrit']['server'],
        config_file['gerrit'].get('vote', False))
    # NOTE(Gonéri): For every review of a component, we
    # - create a version that overwrite the component default origin
    # with a one that is sticked to the review
    # - check if there is some result for the Git review, and if so,
    # push vote
    for patchset in gerrit.list_open_patchsets(
            config_file['gerrit']['project'],
            config_file['gerrit'].get('filter', '')):
        sha = patchset['currentPatchSet']['revision']
        r = dci_client.get('/components', where={'sha': sha})
        components = r.json()
        if components['_meta']['total'] == 0:
            continue
        component = components['_items'][0]
        jobdefinition_components = dci_client.get(
            '/jobdefinition_components', where={'component_id': component['id']}).json()
        from pprint import pprint
        pprint(jobdefinition_components)
        for jobdefinition_component in jobdefinition_components['_items']:
            jobdefinitions = dci_client.get('/jobdefinitions', where={'id': jobdefinition_component['jobdefinition']}).json()
            if len(jobdefinitions['_items']) == 0:
                continue
            jobdefinition = jobdefinitions['_items'][0]
            score = dci_client.get_jobdefinition_score(jobdefinition)
            # TODO(Gonéri): also push a message and the URL to see the job.
            if score != '0':
                print("DCI-CS → Gerrit: %s" % score)
                gerrit.review(
                    patchset['currentPatchSet']['revision'], score)

if __name__ == '__main__':
    main()
