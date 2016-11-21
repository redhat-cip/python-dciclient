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

from __future__ import unicode_literals
import json


def test_show(runner, file_id):
    result = runner.invoke(['file-show', file_id])
    assert 'testsuite errors' in result.output


def test_list(runner, job_id):
    result = runner.invoke(['file-list', '--job-id', job_id])
    files = json.loads(result.output)['files']
    assert len(files) == 1
    assert files[0]['name'] == 'res_junit.xml'


def test_list_without_job_id(runner):
    result = runner.invoke(['file-list'])
    assert 'Error: Missing option "--job-id".' in result.output
