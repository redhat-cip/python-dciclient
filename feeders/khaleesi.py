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
error_message = """
This script make the use of Khaleesi mandatory which is not the current
situation. If you call it know, you will create jobdefinition that are not
compatible with the existing agents.
"""
raise Exception(error_message)
from dciclient.v1.api import component
from dciclient.v1.api import context
from dciclient.v1.api import jobdefinition
from dciclient.v1.api import test

import requests

import time


def _get_timestamp(url):
    """Retrieve a timestamp from the last modified date of the resource."""
    result = requests.get(url)
    last_modified = result.headers['last-modified']
    return time.mktime(time.strptime(last_modified,
                                     '%a, %d %b %Y %H:%M:%S GMT'))


def get_khaleesi_component():
    """Retrieve Khaleesi component"""
    git_url = 'https://github.com/goneri/khaleesi'
    api_url = 'https://api.github.com/repos/goneri/khaleesi/branches/dci'
    commit = requests.get(api_url).json()['commit']

    message = commit['commit']['message']
    title = message.split('\n')[0]
    sha = commit['sha']
    ref = 'dci'
    url = commit['html_url']

    khaleesi_component = {
        "type": component.GIT_COMMIT,
        # leverage the sha to make a unique name
        "name": "[%s][%s]-%s" % ('khaleesi', 'master', sha),
        "title": title,
        "message": message,
        "sha": sha,
        "ref": ref,
        "url": url,
        "git": git_url,
        "canonical_project_name": 'khaleesi'
    }

    return khaleesi_component


def get_khaleesi_settings_component():
    """Retrieve Khaleesi Settings component"""
    git_url = 'file:///khaleesi-settings'

    khaleesi_settings_component = {
        "type": component.GIT_COMMIT,
        "name": "[%s][%s]" % ('khaleesi', 'master'),
        "git": git_url,
        "data": {},
        "canonical_project_name": 'khaleesi-settings'
    }

    return khaleesi_settings_component


def get_khaleesi_installer_component():

    kh_installer_component = {
        "type": component.KH_INSTALLER,
        # TODO(yassine): make a unique name
        "name": 'khaleesi-installer',
        "title": 'Khaleesi installer args',
        "data": {
            'kh_args': {
                'installer': 'rdo_manager',
                'installer-env': 'virthost',
                'installer-images': 'import',
                'installer-network': 'neutron',
                'installer-network-isolation': 'none',
                'installer-network-variant': 'ml2-vxlan',
                'installer-post_action': 'default',
                'installer-topology': 'minimal_no_ceph',
                'installer-tempest': 'smoke',
                'installer-updates': 'none'
            }
        }
    }

    return kh_installer_component


def get_khaleesi_puddle_component():
    url = 'http://download.lab.bos.redhat.com/rel-eng/OpenStack/7.0-RHEL-7'
    timestamp = _get_timestamp('%s/latest/status.txt' % url)

    khaleesi_puddle_component = {
        "type": component.PUDDLE,
        "name": 'Openstack puddle-%s' % timestamp,
        "title": 'Openstack puddle',
        "url": url,
        "data": {
            'kh_args': {
                'product': 'rhos',
                'product-repo': 'puddle',
                'product-version-build': 'latest',
                'product-version': '8_director',
                'extra-vars=product.build': 'latest',
                # TODO(yassine): get dynamically the versions
                'extra-vars=product.repo.puddle_pin_version': '2015-12-03.2',
                'extra-vars=product.repo.puddle_director_pin_version':
                    '2015-12-03.1'
            }
        }
    }

    return khaleesi_puddle_component


def get_test_id(dci_context, name):
    print("Use test '%s'" % name)
    test.create(dci_context, name)
    return test.get(dci_context, name).json()['test']['id']


if __name__ == '__main__':
    dci_context = context.build_dci_context()
    # Create Khaleesi-tempest test
    khaleesi_tempest_test_id = get_test_id(dci_context, 'Khaleesi-tempest')

    components = [get_khaleesi_component(),
                  get_khaleesi_settings_component(),
                  get_khaleesi_installer_component(),
                  get_khaleesi_puddle_component()]

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
        jobdef_name = "Khaleesi - OSP 8 - FV2"
        jobdef = jobdefinition.create(dci_context, jobdef_name,
                                      khaleesi_tempest_test_id)
        if jobdef.status_code == 201:
            jobdef_id = jobdef.json()['jobdefinition']['id']
            for cmpt_id in component_ids:
                jobdefinition.add_component(dci_context, jobdef_id, cmpt_id)
            print("Jobdefinition '%s' created." % jobdef_name)
        else:
            print("Error on jobdefinition creation: '%s'", jobdef.json())
    else:
        print("No jobdefinition created.")
