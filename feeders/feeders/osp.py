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
import dciclient.v1.api.topic as dci_topic

from six.moves.urllib.parse import urlparse

import click
import configparser
import requests


def get_repo_information(repo_file):
    repo_file_raw_content = requests.get(repo_file).text
    config = configparser.ConfigParser()
    config.read_string(repo_file_raw_content)
    # Only use the first section
    section_name = config.sections()[0]
    base_url = config[section_name]["baseurl"].replace("$basearch", "x86_64")
    try:
        version = config[section_name]['version']
    except KeyError:
        # extracting the version from the URL
        version = base_url.split('/')[-4]
    repo_name = config[section_name]['name']
    return base_url, version, repo_name


def get_puddle_component(repo_file, topic_id):
    (base_url, version, repo_name) = get_repo_information(repo_file)

    puddle_type = 'puddle_ospd' if 'director' in repo_name else 'puddle_osp'
    puddle_component = {
        'type': puddle_type,
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


def get_components(urls, topic_id):
    c = []
    for url in urls:
        c += [get_puddle_component(url, topic_id)]
    return c


def build_jobdefinition_name(v, components):
    tmp = []
    for c in components:
        tmp.append("%s %s" % (c['data']['repo_name'], c['data']['version']))
    return 'OSP %s - %s' % (v.split('.')[0], '+'.join(tmp))


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
    versions = [
        {
            'name': '9.0',
            'urls': [
                'http://download.eng.bos.redhat.com/rcm-guest/puddles/OpenStack/9.0-RHEL-7/latest/RH7-RHOS-9.0.repo',  # noqa
                'http://download.eng.bos.redhat.com/rcm-guest/puddles/OpenStack/9.0-RHEL-7-director/latest/RH7-RHOS-9.0-director.repo'],  # noqa
            'topic_id': dci_topic.get(ctx, 'OSP9').json()['topic']['id']
        },
        {
            'name': '8.0',
            'urls': [
                'http://download.eng.bos.redhat.com/rel-eng/OpenStack/8.0-RHEL-7/latest/RH7-RHOS-8.0.repo',  # noqa
                'http://download.eng.bos.redhat.com/rel-eng/OpenStack/8.0-RHEL-7-director/latest/RH7-RHOS-8.0-director.repo'],  # noqa
            'topic_id': dci_topic.get(ctx, 'OSP8').json()['topic']['id']
        }
    ]

    for v in versions:
        # Create Khaleei-tempest test
        components = get_components(v['urls'], v['topic_id'])
        for c in components:
            r = dci_component.create(ctx, **c)
            print(r.status_code)


if __name__ == '__main__':
    main()
