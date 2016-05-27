# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import traceback

from dciclient.v1.api import file
from dciclient.v1.api import job
from dciclient.v1.api import jobdefinition
from dciclient.v1.api import jobstate

import tripleohelper.undercloud


def run_tests(context, undercloud_ip, key_filename):
    undercloud = tripleohelper.undercloud.Undercloud(
        hostname=undercloud_ip,
        user='root',
        key_filename=key_filename)
    undercloud.create_stack_user()

    j = job.get(context, context.last_job_id).json()['job']
    tests = jobdefinition.get_tests(
        context, j['jobdefinition_id']).json()
    try:
        for t in tests['tests']:
            if 'url' not in t['data']:
                continue
            url = t['data']['url']
            undercloud.add_environment_file(
                user='stack',
                filename='overcloudrc')
            undercloud.run('curl -O ' + url, user='stack')
            undercloud.run('bash -x run.sh', user='stack')
            result = undercloud.run(
                'cat result.xml',
                success_status=(0, 1,),
                user='stack')[0]
            file.create(
                context,
                'result.xml',
                result, mime='application/junit',
                job_id=context.last_job_id)
    except Exception:
        msg = traceback.format_exc()
        print(msg)
        jobstate.create(context,
                        'failure',
                        msg,
                        context.last_job_id)
    else:
        jobstate.create(context, 'success', '', context.last_job_id)
