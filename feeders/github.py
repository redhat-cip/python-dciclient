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
from dciclient.v1 import helper

from six.moves.urllib.parse import urlparse

import requests
import sys


def _get_commit_from_tag(account_name, repo_name, tag_value):
    """Retrieve the commit of which a tag was made of"""

    api_url = "https://api.github.com/repos/%s/%s/tags" % (account_name,
                                                           repo_name)
    for tag in requests.get(api_url).json():
        if tag['name'] == tag_value:
            commit = tag['commit']['sha']
            break

    return commit


def _get_commit_from_base_url(url):
    """Retrieve the commit from the canonical url"""

    account_name, repo_name = urlparse(url).path[1:].split('/')
    api_url = "https://api.github.com/repos/%s/%s/branches" % (account_name,
                                                               repo_name)
    for branch in requests.get(api_url).json():
        if branch['name'] == 'master':
            commit = branch['commit']['sha']
            break

    return account_name, repo_name, commit


def get_components(topic_id, url):

    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc == 'github.com':
        raise ValueError("must have a valid Github URL")

    # The code aims to support three distinc forms of URL
    #
    #   * https://github.com/redhat-cip/python-dciclient
    #   * https://github.com/redhat-cip/python-dciclient/commit/XXXXX
    #   * https://github.com/redhat-cip/python-dciclient/tree/0.1.1
    #
    # No matter what is the input form the output form should be
    #
    #  * https://api.github.com/repos/ORGA/REPO/commits/COMMIT
    #
    # The following methods aims to translate from the former to the
    # later
    if len(urlparse(url).path[1:].split('/')) == 2:
        account_name, repo_name, value = _get_commit_from_base_url(url)
    else:
        (account_name, repo_name, commit_type, value) = (
            parsed_url.path[1:].split('/')
        )
        if commit_type == 'tree':
            value = _get_commit_from_tag(account_name, repo_name, value)

    api_url = "https://api.github.com/repos/%s/%s/commits/%s" % (account_name,
                                                                 repo_name,
                                                                 value)
    commit_data = requests.get(api_url).json()

    github_component = {
        "type": component.GIT_COMMIT,
        "name": '%s - %s' % (repo_name, value),
        "canonical_project_name": repo_name,
        "sha": value,
        "title": commit_data['commit']['message'].split('\n')[0],
        "message": commit_data['commit']['message'],
        "url": url,
        "git": 'https://github.com/%s/%s.git' % (account_name, repo_name),
        "topic_id": topic_id
    }

    return [github_component]


def main():
    (options, args) = helper.parse_command_line()

    try:
        topic_id, github_url = args
    except ValueError:
        print('dci-feeder-github topic_id github_commit_url')
        sys.exit(1)

    dci_context = context.build_dci_context(options.dci_cs_url,
                                            options.dci_login,
                                            options.dci_password)

    components = get_components(topic_id, github_url)
    test_id = helper.get_test_id(dci_context, components[0]['name'], topic_id)

    helper.create_jobdefinition_and_add_component(dci_context, components,
                                                  test_id, topic_id)


if __name__ == '__main__':
    main()
