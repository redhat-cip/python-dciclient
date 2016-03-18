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

import ftplib
import re

from dciclient.v1.api import component
from dciclient.v1.api import context
from dciclient.v1 import helper

from six.moves.urllib.parse import urlparse

import click
import re
import requests


def get_repo_information(repo_file_raw_content):
    base_url = re.search('baseurl=((.*)/os)', repo_file_raw_content).group(1)
    base_url = base_url.replace("$basearch", "x86_64")
    version = urlparse(base_url).path.split('/')[5]
    repo_name = urlparse(base_url).path.split('/')[4]

    return base_url, version, repo_name


def get_puddle_component(repo_file_raw_content, topic_id):
    (base_url, version, repo_name) = get_repo_information(repo_file_raw_content)

    # mapping between the repo name from the partners FTP and the internal
    # repositories
    repo_name_mapping = {
        '8.0-RHEL-7': 'RH7-RHOS-8.0',
        '8.0-RHEL-7-director': 'RH7-RHOS-8.0-director'
    }

    puddle_component = {
        'type': component.PUDDLE,
        'canonical_project_name': repo_name,
        'name': '%s %s' % (repo_name, version),
        'url': base_url,
        'data': {
            'path': urlparse(base_url).path,
            'version': version,
            'repo_name': repo_name_mapping[repo_name]
        },
        'topic_id': topic_id,
    }
    return puddle_component


@click.command()
@click.option('--dci-login', envvar='DCI_LOGIN', required=True,
              help="DCI username account.")
@click.option('--dci-password', envvar='DCI_PASSWORD', required=True,
              help="DCI password account.")
@click.option('--dci-cs-url', envvar='DCI_CS_URL', required=True,
              help="DCI CS url.")
@click.option('--dci-topic-id', envvar='DCI_TOPIC_ID', required=True,
              help="DCI topic id.")
@click.option('--partner-token', required=True,
              help="partner FTP token.")
def main(dci_login, dci_password, dci_cs_url, dci_topic_id, partner_token):
    dci_context = context.build_dci_context(dci_cs_url, dci_login,
                                            dci_password)

    # Create Khaleesi-tempest test
    test_id = helper.get_test_id(dci_context, 'tempest', dci_topic_id)
    server = 'partners.redhat.com'
    base_dir = '/' + partner_token + '/OpenStack/8.0'

    ftp = ftplib.FTP(server)
    ftp.login()
    ftp.cwd(base_dir)
    beta = {}

    repo_file_mapping = {
        'OSP-8': 'RH7-RHOS-8.0.repo',
        'OSP-8-director': 'RH7-RHOS-8.0-director.repo',
    }

    for i in ftp.nlst():
        m = re.search('(OSP-8-director|OSP-8)-Beta-(\d+)', i)
        if not m:
            continue
        directory = m.group(0)
        repo_type = m.group(1)  # OSP-8 / OSP-8-director
        version = int(m.group(2))  # 8
        if version not in beta:
            beta[version] = {}
        beta[version][repo_type] = directory

    cur = {}
    for v in sorted(beta):
        cur.update(beta[v])
        components = []
        for repo_type, directory in cur.items():
            repo_file = repo_file_mapping[repo_type]
            lines = []
            ftp.retrlines('retr ' + base_dir + '/' + directory + '/' + repo_file, lines.append)
            repo_file_raw_content = '\n'.join(lines)

            c = get_puddle_component(
                repo_file_raw_content,
                dci_topic_id)
            components.append(c)

        tmp = [c['data']['repo_name'] + ' ' + c['data']['version'] for c in components]
        jobdef_name = 'OSP 8 - ' + '+'.join(tmp)
        helper.create_jobdefinition_and_add_component(dci_context, components,
                                                      test_id, dci_topic_id,
                                                      jobdef_name=jobdef_name)


if __name__ == '__main__':
    main()
