#!/usr/bin/env python
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

from dciclient.v1.api import context as dci_context
from dciclient.v1.api import file as dci_file
from dciclient.v1.api import job as dci_job
from dciclient.v1.api import jobstate as dci_jobstate
from dciclient.v1.api import remoteci as dci_remoteci
from dciclient.v1.api import topic as dci_topic
from dciclient.v1 import helper as dci_helper
from dciclient.v1 import tripleo_helper as dci_tripleo_helper

import tripleohelper.server
import tripleohelper.undercloud

import argparse
import logging
from pprint import pprint
import sys
import traceback
import yaml


def load_config(config_path):
    with open(config_path, 'r') as fd:
        dci_conf = yaml.load(fd)
    pprint(dci_conf)
    return dci_conf


def get_dci_context(**auth):
    return dci_context.build_dci_context(**auth)


def main(argv=None):
    repo_entry = """
[{name}]
name={name}
baseurl={mirror_url}{path}
enable=1
gpgcheck=0
priority=0

"""
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic')
    parser.add_argument('--config', default='/etc/dci/dci_agent.yaml')
    args = parser.parse_args(argv)

    dci_conf = load_config(args.config)
    if 'dci_cs_url' not in dci_conf['auth']:
        dci_conf['auth'] = 'https://api.distributed-ci.io'

    ctx = get_dci_context(**dci_conf['auth'])
    topic_name = args.topic if args.topic else dci_conf['topic']
    topic = dci_topic.get(ctx, topic_name).json()['topic']
    print(dci_conf)
    print(dci_conf['remoteci'])
    remoteci = dci_remoteci.get(ctx, dci_conf['remoteci']).json()['remoteci']
    print(remoteci)
    r = dci_job.schedule(ctx, remoteci['id'], topic_id=topic['id'])
    if r.status_code == 412:
        print('Nothing to do')
        exit(0)
    elif r.status_code != 201:
        print('Unexpected code: %d' % r.status_code)
        print(r.text)
        exit(1)
    job_full_data = dci_job.get_full_data(ctx, ctx.last_job_id)
    pprint(job_full_data)

    dci_jobstate.create(ctx, 'pre-run', 'refreshing local mirror',
                        ctx.last_job_id)
    mirror_location = dci_conf['mirror'].get('directory', '/var/www/html')
    try:
        with open(mirror_location + '/RHOS-DCI.repo', 'w') as f:
            for component in job_full_data['components']:
                dci_helper.run_command(
                    ctx,
                    [
                        'rsync',
                        '-av',
                        '--hard-links',
                        'partner@rhos-mirror.distributed-ci.io:/srv/puddles/' +
                        component['data']['path'] + '/',
                        '/var/www/html' + component['data']['path']])
                f.write(repo_entry.format(
                    mirror_url=dci_conf['mirror']['url'],
                    name=component['data']['repo_name'],
                    path=component['data']['path']))

        dci_jobstate.create(ctx, 'pre-run', 'director node provisioning',
                            ctx.last_job_id)
        dci_helper.run_command(ctx, dci_conf['commands']['provisioning'],
                               shell=True)
        # Waiting for the undercloud host to be back
        undercloud = tripleohelper.undercloud.Undercloud(
            hostname=dci_conf['undercloud_ip'],
            user='stack',
            key_filename=dci_conf['key_filename'])
        undercloud.run('sudo mkdir /root/.ssh', retry=600, user='stack')
        undercloud.run('sudo chmod 700 /root/.ssh', user='stack')
        undercloud.run('sudo cp /home/stack/.ssh/authorized_keys /root/.ssh/',
                       user='stack')
        dci_jobstate.create(
            ctx,
            'running',
            'undercloud deployment',
            ctx.last_job_id)
        dci_helper.run_command(ctx, dci_conf['commands']['undercloud'],
                               shell=True)
        dci_jobstate.create(ctx, 'running', 'overcloud deployment',
                            ctx.last_job_id)
        dci_helper.run_command(ctx, dci_conf['commands']['overcloud'],
                               shell=True)
        dci_tripleo_helper.run_tests(
            ctx,
            undercloud_ip='192.168.100.10',
            stack_name='lab2',
            key_filename=dci_conf['key_filename'])
    except Exception as e:
        dci_jobstate.create(ctx, 'failure', 'An exception occured.',
                            ctx.last_job_id)
        content = traceback.format_exc()
        print(content)
        dci_file.create(ctx, 'error', str(e), mime='text/plain',
                        jobstate_id=ctx.last_jobstate_id)
        dci_file.create(ctx, 'backtrace', content, mime='text/plain',
                        jobstate_id=ctx.last_jobstate_id)

if __name__ == '__main__':
    main()
