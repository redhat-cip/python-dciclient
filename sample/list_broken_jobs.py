# -*- encoding: utf-8 -*-
#
# Copyright 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from datetime import datetime
from dciclient.v1.api import context as dci_context
from dciclient.v1.api import job as dci_job
from dciclient.v1.utils import str2date

ctx = dci_context.build_dci_context()


for j in dci_job.iter(ctx):
    age = datetime.utcnow() - str2date(j['created_at'])

    if age.total_seconds() < 3600 * 3:
        continue

    url = 'https://www.distributed-ci.io/#!/jobs/%s/results' % j['id']
    jobstates = dci_job.list_jobstates(ctx, id=j['id'], ).json()['jobstates']
    if len(jobstates) < 2:
        print('no log: ' + url)
        continue

    end = str2date(jobstates[-1]['created_at'])
    begin = str2date(jobstates[0]['created_at'])
    duration = end - begin
    if age.total_seconds() < 3600 * 3:
        continue
    if duration.total_seconds() < 60 * 5:
        print('below 5 minutes: %s (duration: %s)' % (url, j['id'], duration))

    if duration.total_seconds() > 3600 * 10:
        print('above 10 hours: %s (duration: %s)' % (url, j['id'], duration))
