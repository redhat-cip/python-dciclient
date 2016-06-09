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

import dciclient.v1.api.component as dci_component
import dciclient.v1.api.context as dci_context
import dciclient.v1.api.test as dci_test
import dciclient.v1.api.topic as dci_topic
import dciclient.v1.helper as dci_helper

from six.moves.urllib.parse import urlparse

import click
import re
import requests


def get_repo_information(repo_file):
    repo_file_raw_content = requests.get(repo_file).text
    base_url = re.search('baseurl=((.*)/os)', repo_file_raw_content).group(1)
    base_url = base_url.replace("$basearch", "x86_64")
    version = urlparse(base_url).path.split('/')[4]
    repo_name = urlparse(base_url).path.split('/')[5]

    return base_url, version, repo_name


def get_puddle_component(repo_file, topic_id):
    (base_url, version, repo_name) = get_repo_information(repo_file)

    puddle_component = {
        'type': dci_component.PUDDLE,
        'canonical_project_name': repo_name,
        'name': '%s %s' % (repo_name, version),
        'url': base_url,
        'data': {
            'path': urlparse(base_url).path,
            'version': version,
            'repo_name': repo_name
        },
        'topic_id': topic_id,
    }
    return puddle_component


def get_test_ids(ctx, topic_id):
    test_list = dci_test.list(ctx, topic_id=topic_id).json()['tests']
    test_ids = [test['id'] for test in test_list]
    return test_ids


def get_components(v, topic_id):
    base_url = "http://download.eng.bos.redhat.com/rel-eng/OpenStack/"
    osp_url = (
        "{base_url}{version}"
        "-RHEL-7/latest/RH7-RHOS-{version}.repo")
    ospd_url = (
        "{base_url}{version}"
        "-RHEL-7-director/latest/RH7-RHOS-{version}-director.repo")
    components = [
        get_puddle_component(
            osp_url.format(version=v, base_url=base_url),
            topic_id)]

    if v == '8.0':
        # OSP8 comes also with the addictional director repository
        ospd = get_puddle_component(
            ospd_url.format(version=v, base_url=base_url),
            topic_id)
        components.append(ospd)
    return components


def build_jobdefinition_name(v, components):
    tmp = []
    for c in components:
        tmp.append(c['data']['repo_name'] + ' ' + c['data']['version'])
    return 'OSP ' + v.split('.')[0] + ' - ' + '+'.join(tmp)


@click.command()
@click.option('--dci-login', envvar='DCI_LOGIN', required=True,
              help="DCI username account.")
@click.option('--dci-password', envvar='DCI_PASSWORD', required=True,
              help="DCI password account.")
@click.option('--dci-cs-url', envvar='DCI_CS_URL', required=True,
              help="DCI CS url.")
def main(dci_login, dci_password, dci_cs_url):
    ctx = dci_context.build_dci_context(dci_cs_url, dci_login,
                                        dci_password)

    versions = {
        dci_topic.get(ctx, 'OSP8').json()['topic']['id']: '8.0',
        dci_topic.get(ctx, 'OSP9').json()['topic']['id']: '9.0'
    }
    for topic_id, v in versions.items():
        # Create Khaleesi-tempest test
        components = get_components(v, topic_id)

        dci_helper.create_jobdefinition(
            ctx,
            components,
            get_test_ids(ctx, topic_id),
            topic_id,
            jobdef_name=build_jobdefinition_name(v, components))

if __name__ == '__main__':
    main()
