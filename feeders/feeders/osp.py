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
from dciclient.v1 import helper

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
        'type': component.PUDDLE,
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

    # Create Khaleesi-tempest test
    test_id = helper.get_test_id(dci_context, 'tempest', dci_topic_id)

    components = [
        # TODO(Gonéri): We should also return the images.
        get_puddle_component(
            'http://download.eng.bos.redhat.com/rel-eng/OpenStack/' +
            '8.0-RHEL-7-director/latest/RH7-RHOS-8.0-director.repo',
            dci_topic_id),
        get_puddle_component(
            'http://download.eng.bos.redhat.com/rel-eng/OpenStack/' +
            '8.0-RHEL-7/latest/RH7-RHOS-8.0.repo',
            dci_topic_id)]

    helper.create_jobdefinition_and_add_component(dci_context, components,
                                                  test_id, dci_topic_id)

if __name__ == '__main__':
    main()
