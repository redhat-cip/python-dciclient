# -*- encoding: utf-8 -*-
#
# Copyright 2016 Red Hat, Inc.
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

from dciclient.v1.api import job


def test_job_updated(dci_context, job_id):
    new_configuration = {'foo': 'bar'}
    j = job.get(dci_context, job_id).json()['job']
    assert j['configuration'] == {}
    job.update(dci_context, id=job_id, etag=j['etag'],
               configuration=new_configuration)
    r = job.get(dci_context, job_id)
    j = r.json()['job']
    assert j['configuration'] == new_configuration
