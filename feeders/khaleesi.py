# Copyright 2015 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from dciclient.v1.consumers import feeder
import json
import requests


DCI_LOGIN='admin'
DCI_PASSWORD='admin'
DCI_CS_URL='http://dci.enovance.com'

COMPONENTTYPES = ['git_commit', 'repo']
TEST = 'khaleesi_test'


def get_khaleesi(componenttype):
    """Retrieve Khaleesi component"""
    url = 'https://api.github.com/repos/redhat-openstack/khaleesi/branches/master'
    git_url = 'https://github.com/redhat-openstack/khaleesi'

    commit = requests.get(url).json()['commit']

    title = commit['commit']['message'].split('\n')[0]
    message = 'test' # commit['commit']['message']
    sha = commit['sha']
    url = commit['html_url']

    component = {
        "componenttype_id": componenttype,
        "name": "[%s][%s] %s" % ('khaleesi', 'master', title),
        "title": title,
        "message": message,
        "sha": sha,
        "url": url,
        "git": git_url,
        "data": {},
        "canonical_project_name": 'khaleesi'
    }

    return component

def get_khaleesi_settings(componenttype):
    """Retrieve Khaleesi Settings component"""
    url = 'https://api.github.com/repos/redhat-openstack/khaleesi-settings/branches/master'
    #git_url = 'https://github.com/redhat-openstack/khaleesi-settings'
    git_url = 'https://code.engineering.redhat.com/gerrit/khaleesi-settings'

    commit = requests.get(url).json()['commit']

    title = commit['commit']['message'].split('\n')[0]
    message =  'test' #commit['commit']['message']
    sha = commit['sha']
    url = commit['html_url']

    component = {
        "componenttype_id": componenttype,
        "name": "[%s][%s] %s" % ('khaleesi', 'master', title),
        "title": title,
        "message": message,
        "sha": sha,
        "url": url,
        "git": git_url,
        "data": {},
        "canonical_project_name": 'khaleesi-settings'
    }

    return component

def get_osp_repo(componenttype):
    """Retrieve OSP repo"""
    url = 'http://download.eng.bos.redhat.com/rel-eng/OpenStack/8.0-RHEL-7/latest/RH7-RHOS-8.0.repo'

    component = {
        "componenttype_id": componenttype,
        "name": 'OSP Repo latest release',
        "title": 'OSP Repo latest release',
        "url": url,
        "data": {},
        "canonical_project_name": 'osp'
    }

    return component

def get_ospd_repo(componenttype):
    """Retrieve OSP-Director repo"""
    url = 'http://download.eng.bos.redhat.com/rel-eng/OpenStack/8.0-RHEL-7-director/latest/RH7-RHOS-8.0-director.repo'

    component = {
        "componenttype_id": componenttype,
        "name": 'OSP-director Repo latest release',
        "title": 'OSP-director Repo latest release',
        "url": url,
        "data": {},
        "canonical_project_name": 'ospd'
    }

    return component

if __name__ == '__main__':
    l_feeder = feeder.Feeder(DCI_CS_URL, DCI_LOGIN, DCI_PASSWORD)
    components = []

    componenttypes = l_feeder.ensure_componenttype(COMPONENTTYPES)
    test_id = l_feeder.ensure_test(TEST)

    components.append(get_khaleesi(componenttypes['git_commit']))
    components.append(get_khaleesi_settings(componenttypes['git_commit']))

    components.append(get_osp_repo(componenttypes['repo']))
    components.append(get_ospd_repo(componenttypes['repo']))

    for component in components:
        l_feeder.create_component(component)

    l_feeder.create_jobdefinition('Khaleesi', test_id)
