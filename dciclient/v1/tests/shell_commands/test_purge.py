# -*- encoding: utf-8 -*-
#
# Copyright 2015-2017 Red Hat, Inc.
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


def test_purge_noop(runner, dci_context, remoteci_id):
    runner.invoke(['topic-create', '--name', 'osp'])
    runner.invoke(['topic-create', '--name', 'osp2'])
    topics = runner.invoke(['topic-list'])['topics']
    topic_id = topics[0]['id']
    assert len(topics) == 2

    runner.invoke(['topic-delete', topic_id])
    topics = runner.invoke(['topic-list'])['topics']
    assert len(topics) == 1

    purge_res = runner.invoke(['purge', '--resources', 'topics',
                               '--noop'])['topics']
    assert purge_res[0]['id'] == topic_id
    assert purge_res[0]['state'] == 'archived'

    runner.invoke(['purge', '--resources', 'topics'])

    purge_res = runner.invoke(['purge', '--resources', 'topics',
                               '--noop'])['topics']
    assert len(purge_res) == 0

    topics = runner.invoke(['topic-list'])['topics']
    assert len(topics) == 1
