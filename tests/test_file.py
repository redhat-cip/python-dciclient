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


import dciclient.v1.api.file as dci_file


def test_iter(dci_context, job_id):
    f_names = ['file_%d' % i for i in range(100)]
    for name in f_names:
        dci_file.create(
            dci_context, name=name,
            content='some content', mime='plain/text',
            job_id=job_id)
    cpt = 0
    seen_names = []
    for f in dci_file.iter(dci_context):
        seen_names.append(f['name'])
        cpt += 1
    # job already comes with 2 files
    all_files = len(dci_file.list(dci_context).json()['files'])
    assert all_files == 100 + 2
    assert cpt == 100 + 2
    assert len(set(seen_names) - set(f_names)) == 2
