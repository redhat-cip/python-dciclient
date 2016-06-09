# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Red Hat, Inc
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

import json
import tripleohelper.undercloud


def push_stack_details(context, undercloud):
    undercloud.yum_install(['git'])
    repo_url = 'https://github.com/goneri/tripleo-stack-dump'
    undercloud.run(
        'test -d tripleo-stack-dump || git clone ' + repo_url,
        user='stack')
    undercloud.add_environment_file(
        user='stack',
        filename='stackrc')
    undercloud.run('./tripleo-stack-dump/tripleo-stack-dump', user='stack')
    with undercloud.open('/home/stack/tripleo-stack-dump.json') as fd:
        j = job.get(
            context,
            id=context.last_job_id).json()['job']
        job.update(
            context,
            id=context.last_job_id,
            etag=j['etag'],
            configuration=json.load(fd))


def run_tests(context, undercloud_ip, key_filename, user='root'):
    undercloud = tripleohelper.undercloud.Undercloud(
        hostname=undercloud_ip,
        user=user,
        key_filename=key_filename)
    undercloud.create_stack_user()

    final_status = 'success'
    if undercloud.run(
            'test -f stackrc',
            user='stack',
            success_status=(0, 1,))[1] != 0:
        msg = 'undercloud deployment failure'
        jobstate.create(context, 'failure', msg, context.last_job_id)
        return
    push_stack_details(context, undercloud)
    if undercloud.run(
            'test -f overcloudrc',
            user='stack',
            success_status=(0, 1,))[1] != 0:
        msg = 'overcloud deployment failure'
        jobstate.create(context, 'failure', msg, context.last_job_id)
        return

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
            with undercloud.open('result.xml') as fd:
                file.create(
                    context,
                    'result.xml',
                    fd.read(), mime='application/junit',
                    job_id=context.last_job_id)
    except Exception:
        msg = traceback.format_exc()
        print(msg)
    else:
        msg = 'test(s) success'
    jobstate.create(context, final_status, msg, context.last_job_id)
