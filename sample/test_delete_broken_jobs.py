# -*- encoding: utf-8 -*-
#
# Copyright 2017 Red Hat, Inc.
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

import delete_broken_jobs


def test_delete_broken_jobs_no_jobstate():
    j = {
        'id': 1,
        'created_at': '2017-06-19T05:14:55.425411',
        'jobstates': []
    }
    assert delete_broken_jobs.is_broken(j) is True


def test_delete_broken_jobs_to_short():
    j = {
        'id': 1,
        'created_at': '2017-06-19T05:14:55.425411',
        'jobstates': [
            {
                'created_at': '2017-06-19T05:16:55.425411',
            }]
    }
    assert delete_broken_jobs.is_broken(j) is True


def test_delete_broken_jobs_to_long():
    j = {
        'id': 1,
        'created_at': '2017-05-19T05:14:55.425411',
        'jobstates': [
            {
                'created_at': '2017-06-19T05:14:55.425411',
            }]
    }
    assert delete_broken_jobs.is_broken(j) is True
