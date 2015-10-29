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

import argparse
import os
import re
import sys
import yaml

import requests

from agents.utils import gerritlib
from dciclient import v1 as client_v1


def register_github_commit(gh_s, dci_client, componenttype, canonical_project_name, github_account, branch_name):
    branch = gh_s.get(
        'https://api.github.com/repos/' + github_account + '/' + canonical_project_name + '/branches/' + branch_name).json()
    commit = branch['commit']
    sha = commit['sha']
    url = commit['html_url']
    title = commit['commit']['message'].split('\n')[0]
    message = commit['commit']['message']
    git_url = 'https://github.com/' + github_account + '/' + canonical_project_name

    version_data = {
        "componenttype_id": componenttype['id'],
        "name": "[%s][%s] %s" % (canonical_project_name, branch_name, title),
        "title": title,
        "message": message,
        "sha": sha,
        "url": url,
        # TODO(Gonéri): We use components/$name/ref now
        "git": git_url,
        "data": {},
        "canonical_project_name": canonical_project_name
    }
    component = dci_client.find_or_create_or_refresh(
        '/components', version_data, unicity_key=['sha'])
    return component


def register_delorean_snapshot(dci_client, componenttype, url, canonical_project_name):
    r = requests.get(url)
    m = re.search(r'name=(.+-([^-]*))$', r.text,  re.MULTILINE)
    name = m.group(1)
    version = m.group(1)
    component = dci_client.find_or_create_or_refresh(
        '/components', {
            'name': name,
            'canonical_project_name': canonical_project_name,
            'componenttype_id': componenttype['id'],
            'data': {
                'ksgen_args': {
                    'extra-vars': {
                        'product.repo.poodle_pin_version:': version,
                    }}}}, unicity_key=['name'])
    return component


def get_gerrit_review_as_component(
        dci_client,
        componenttype,
        canonical_project_name,
        git_url,
        gerrit_server,
        gerrit_project,
        gerrit_filter=''):
    gerrit = gerritlib.Gerrit(gerrit_server)
    for patchset in gerrit.list_open_patchsets(gerrit_project, gerrit_filter):
        title = patchset['commitMessage'].split('\n')[0]
        message = patchset['commitMessage']
        gerrit_id = patchset['id']
        url = patchset['url']
        ref = patchset['currentPatchSet']['ref']
        sha = patchset['currentPatchSet']['revision']
        print("Gerrit to DCI-CS: %s" % title)
        version_data = {
            "componenttype_id": componenttype['id'],
            "name": "[gerrit] %s - %s" % (canonical_project_name, title),
            "title": title,
            "message": message,
            "sha": sha,
            "url": url,
            "git": git_url,
            "ref": ref,
            "data": {
                "gerrit_id": gerrit_id,
            },
            "canonical_project_name": canonical_project_name
        }
        component = dci_client.find_or_create_or_refresh(
            '/components', version_data, unicity_key=['sha'])
        yield component

##############################################
##############################################
##############################################

def init_conf():
    parser = argparse.ArgumentParser(description='Gerrit agent.')
    parser.add_argument("--config-file", action="store",
                        help="the configuration file path")
    conf = parser.parse_args()
    return yaml.load(open(conf.config_file).read())


def main():
    config_file = init_conf()
    dci_client = client_v1.DCIClient()
    componenttypes = {
        'git_commit': dci_client.find_or_create_or_refresh(
            '/componenttypes',
            {"name": 'git_commit'}),
        'repo': dci_client.find_or_create_or_refresh(
            '/componenttypes',
            {"name": 'poodle'})}
    test = dci_client.find_or_create_or_refresh(
        '/tests',
# TODO(Gonéri): tests.name is also used by the agent to identify the kind of job they can
# process. We must fix that.
        config_file['test'])

    gh_s = requests.Session()
    gh_s.headers.setdefault(
        'Authorization', 'token %s' % os.environ['GITHUB_TOKEN'])

    base_components = [
        register_github_commit(
            gh_s,
            dci_client,
            componenttypes['git_commit'],
            canonical_project_name='khaleesi-settings',
            github_account='redhat-openstack',
            branch_name='master'),
        register_delorean_snapshot(
            dci_client,
            componenttypes['repo'],
            canonical_project_name='RDO_Mgnt_Development',
            url='http://trunk-mgt.rdoproject.org/centos-kilo/current/delorean-rdo-management.repo')]

    # Push the current Khaleesi master
    khaleesi_master = register_github_commit(
        gh_s,
        dci_client,
        componenttypes['git_commit'],
        canonical_project_name='khaleesi',
        github_account='redhat-openstack',
        branch_name='master')
    dci_client.create_jobdefinition(test, None, base_components + [khaleesi_master])

    # Push the last Gerrit review
    for component in get_gerrit_review_as_component(
            dci_client,
            componenttypes['git_commit'],
            canonical_project_name=config_file['gerrit']['canonical_project_name'],
            git_url=config_file['gerrit']['git_url'],
            gerrit_server=config_file['gerrit']['server'],
            gerrit_project=config_file['gerrit']['project'],
            gerrit_filter=config_file['gerrit']['filter']):
        dci_client.create_jobdefinition(test, None, base_components + [component])


if __name__ == '__main__':
    main()
