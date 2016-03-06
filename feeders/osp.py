#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2015-2016 Red Hat, Inc.
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
from dciclient.v1.api import topic

import configparser
import requests
from urllib.parse import urlparse


def get_puddle_component(repo_file, repo_name):
    repo_file_raw_content = requests.get(repo_file).text
    config = configparser.ConfigParser()
    config.read_string(repo_file_raw_content)
    base_url = config[repo_name]['baseurl'].replace("$basearch", "x86_64")
    o = urlparse(base_url)
    path = o.path
    version = path.split('/')[4]

    puddle_component = {
        'type': component.PUDDLE,
        'canonical_project_name': repo_name,
        'name': '%s %s' % (repo_name, version),
        'url': base_url,
        'data': {
            'path': path,
            'version': version,
            'repo_name': repo_name
        }
    }
    return puddle_component


def get_test_id(dci_context, name, topic_id):
    test.create(dci_context, name, topic_id)
    return test.get(dci_context, name).json()['test']['id']


if __name__ == '__main__':
    dci_context = context.build_dci_context()
    # Create Khaleesi-tempest test
    topic_id = topic.get(dci_context, 'default').json()['topic']['id']
    test_id = get_test_id(dci_context, 'tempest', topic_id)

    components = [
        # TODO(Gonéri): We should also return the images.
        get_puddle_component(
            'http://download.eng.bos.redhat.com/rel-eng/OpenStack/' +
            '8.0-RHEL-7-director/latest/RH7-RHOS-8.0-director.repo',
            'RH7-RHOS-8.0-director'),
        get_puddle_component(
            'http://download.eng.bos.redhat.com/rel-eng/OpenStack/' +
            '8.0-RHEL-7/latest/RH7-RHOS-8.0.repo',
            'RH7-RHOS-8.0')]

    # If at least one component doesn't exist in the database then a new
    # jobdefinition must be created.
    at_least_one = False
    component_ids = []
    names = []
    for cmpt in components:
        names.append(cmpt['name'])
        created_cmpt = component.create(dci_context, topic_id=topic_id, **cmpt)
        if created_cmpt.status_code == 201:
            at_least_one = True
        elif created_cmpt.status_code == 422:
            created_cmpt = component.get(dci_context, cmpt['name'])
        component_ids.append(created_cmpt.json()['component']['id'])

    if at_least_one:
        jobdef_name = 'OSP 8 - %s' % '+'.join(names)
        jobdef = jobdefinition.create(
            dci_context,
            jobdef_name,
            topic_id=topic_id,
            test_id=test_id)
        if jobdef.status_code == 201:
            jobdef_id = jobdef.json()['jobdefinition']['id']
            for cmpt_id in component_ids:
                jobdefinition.add_component(dci_context, jobdef_id, cmpt_id)
            print("Jobdefinition '%s' created." % jobdef_name)
        else:
            print("Error on jobdefinition creation: '%s'", jobdef.json())
    else:
        print("No jobdefinition created.")
