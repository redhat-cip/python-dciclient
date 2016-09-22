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
from dciclient.v1.api import remoteci
from dciclient.v1.logger import DciHandler

import json
import logging
import requests.packages.urllib3
import tripleohelper.undercloud


def push_stack_details(context, undercloud, stack_name='overcloud'):
    undercloud.yum_install(['git'])
    repo_url = 'https://github.com/goneri/tripleo-stack-dump'
    undercloud.run(
        'test -d tripleo-stack-dump || git clone ' + repo_url,
        user='stack')
    undercloud.add_environment_file(
        user='stack',
        filename='stackrc')
    undercloud.run(
        './tripleo-stack-dump/list_nodes_status',
        user='stack')
    undercloud.run(
        './tripleo-stack-dump/tripleo-stack-dump ' + stack_name,
        user='stack')
    with undercloud.open('/home/stack/tripleo-stack-dump.json') as fd:
        j = job.get(
            context,
            id=context.last_job_id).json()['job']
        job.update(
            context,
            id=context.last_job_id,
            etag=j['etag'],
            configuration=json.load(fd))


def run_tests(context, undercloud_ip, key_filename, remoteci_id,
              user='root', stack_name='overcloud'):

    # Retrieve the certification_id data field. In order to run
    # the rhcert test suite if enabled. If absent set to empty string.
    data = remoteci.get_data(
        context, remoteci_id, ['certification_id']).json()
    certification_id = data and data.get('certification_id', '')

    # redirect the log messages to the DCI Control Server
    # https://github.com/shazow/urllib3/issues/523
    requests.packages.urllib3.disable_warnings()
    dci_handler = DciHandler(context)
    logger = logging.getLogger('tripleohelper')
    logger.addHandler(dci_handler)

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
    push_stack_details(context, undercloud, stack_name=stack_name)
    rcfile = stack_name + 'rc'
    if undercloud.run(
            'test -f ' + rcfile,
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
            jobstate.create(
                context,
                'running',
                'Running test ' + t['name'],
                context.last_job_id)
            url = t['data']['url']
            undercloud.add_environment_file(
                user='stack',
                filename=rcfile)
            undercloud.run('curl -O ' + url, user='stack')
            undercloud.run((
                'DCI_CERTIFICATION_ID=%s '
                'DCI_REMOTECI_ID=%s '
                'DCI_JOB_ID=%s '
                'DCI_OVERCLOUD_STACK_NAME=%s '
                'bash -x run.sh') % (
                    certification_id,
                    remoteci_id,
                    j['id'],
                    stack_name), user='stack')
            with undercloud.open('result.xml', user='stack') as fd:
                file.create(
                    context,
                    t['name'],
                    fd.read(), mime='application/junit',
                    job_id=context.last_job_id)
    except Exception:
        msg = traceback.format_exc()
        final_status = 'failure'
        print(msg)
    else:
        msg = 'test(s) success'
    jobstate.create(context, final_status, msg, context.last_job_id)
