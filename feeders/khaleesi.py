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
    git_url = 'https://github.com/redhat-openstack/khaleesi'
    api_url = ("https://api.github.com/repos/redhat-openstack/khaleesi/"
               "branches/master")
    commit = requests.get(api_url).json()['commit']

    message = commit['commit']['message']
    title = message.split('\n')[0]
    sha = commit['sha']
    url = commit['html_url']

    khaleesi_component = {
        "type": 'git_commit',
        # leverage the sha to make a unique name
        "name": "[%s][%s]-%s" % ('khaleesi', 'master', sha),
        "title": title,
        "message": message,
        "sha": sha,
        "url": url,
        "git": git_url,
        "data": {},
        "canonical_project_name": 'khaleesi'
    }

    return khaleesi_component


def get_khaleesi_settings_component():
    """Retrieve Khaleesi Settings component"""
    git_url = 'https://code.engineering.redhat.com/gerrit/khaleesi-settings'
    api_url = ("https://api.github.com/repos/redhat-openstack/"
               "khaleesi-settings/branches/master")
    commit = requests.get(api_url).json()['commit']

    message = commit['commit']['message']
    title = message.split('\n')[0]
    sha = commit['sha']
    url = commit['html_url']

    khaleesi_settings_component = {
        "type": 'git_commit',
        # leverage the sha to make a unique name
        "name": "[%s][%s]-%s" % ('khaleesi', 'master', sha),
        "title": title,
        "message": message,
        "sha": sha,
        "url": url,
        "git": git_url,
        "data": {},
        "canonical_project_name": 'khaleesi-settings'
    }

    return khaleesi_settings_component


def get_osp_repo_component():
    """Retrieve OSP repo"""
    url = ("http://download.eng.bos.redhat.com/rel-eng/OpenStack/8.0-RHEL-7"
           "/latest/RH7-RHOS-8.0.repo")
    timestamp = _get_timestamp("http://download.eng.bos.redhat.com/rel-eng/"
                               "OpenStack/8.0-RHEL-7/latest/status.txt")

    osp_component = {
        "type": 'repo',
        "name": 'osp-%s' % timestamp,
        "title": 'OSP release',
        "url": url,
        "data": {},
        "canonical_project_name": 'osp'
    }

    return osp_component


def get_ospd_repo_component():
    """Retrieve OSP-Director repo"""
    url = ("http://download.eng.bos.redhat.com/rel-eng/OpenStack/"
           "8.0-RHEL-7-director/latest/RH7-RHOS-8.0-director.repo")
    timestamp = _get_timestamp("http://download.eng.bos.redhat.com/rel-eng/"
                               "OpenStack/8.0-RHEL-7-director/latest/"
                               "status.txt")

    ospd_component = {
        "type": 'repo',
        "name": 'ospd-%s' % timestamp,
        "title": 'OSP-Director release',
        "url": url,
        "data": {},
        "canonical_project_name": 'ospd'
    }

    return ospd_component


if __name__ == '__main__':
    dci_context = context.build_dci_context()
    components = [get_khaleesi_component(),
                  get_khaleesi_settings_component(),
                  get_osp_repo_component(),
                  get_ospd_repo_component()]

    at_least_one = False
    for cmpt in components:
        print("Create component '%s', type '%s'" % (cmpt['name'],
                                                    cmpt['type']))
        created_cmpt = component.create(dci_context, **cmpt)
        if created_cmpt.status_code == 201:
            at_least_one = True

    if at_least_one:
        jobdef = jobdefinition.create(dci_context, 'Khaleesi - OSP 8 - FV2')
        print("job def created")
    else:
        print("job def not created")

