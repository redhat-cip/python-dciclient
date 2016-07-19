#!/usr/bin/env python

from dciclient.v1.api import context as dci_context
from dciclient.v1.api import file as dci_file
from dciclient.v1.api import job as dci_job
from dciclient.v1.api import jobstate as dci_jobstate
from dciclient.v1 import helper as dci_helper
from dciclient.v1 import tripleo_helper as dci_tripleo_helper
from dciclient.v1.api import topic as dci_topic

import tripleohelper.server
import tripleohelper.undercloud

import argparse
import logging
from pprint import pprint
import subprocess
import sys
import traceback
import yaml


def load_config(config_path):
    with open(config_path, 'r') as fd:
        dci_conf = yaml.load(fd)
    pprint(dci_conf)
    return dci_conf


def get_dci_context(**auth):
    ctx = dci_context.build_dci_context(**auth)


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
    parser.add_argument('--topic', default='OSP8')
    parser.add_argument('--config', default='/etc/dci/dci_agent.yaml')
    args = parser.parse_args(argv)

    dci_conf = load_config(args.config)

    ctx = get_dci_context(**dci_conf['auth'])
    print(dci_topic.get(ctx, args.topic).text)
    topic = dci_topic.get(ctx, args.topic).json()['topic']
    r = dci_job.schedule(ctx, dci_conf['remoteci_id'], topic_id=topic['id'])
    if r.status_code == 412:
        print('Nothing to do')
        exit(0)
    job_full_data = dci_job.get_full_data(ctx, ctx.last_job_id)
    pprint(job_full_data)

    dci_jobstate.create(ctx, 'pre-run', 'refreshing local mirror', ctx.last_job_id)
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
                        'rsync@hos-mirror.distributed-ci.io:/var/www/html' + component['data']['path'] + '/',
                        '/var/www/html' + component['data']['path']])
                f.write(repo_entry.format(
                    mirror_url=dci_conf['mirror']['url'],
                    name=component['data']['repo_name'],
                    path=component['data']['path']))

        dci_jobstate.create(ctx, 'pre-run', 'director node provisioning', ctx.last_job_id)
        dci_helper.run_command(ctx, dci_conf['commands']['provisioning'], shell=True)
        # Waiting for the undercloud host to be back
        undercloud = tripleohelper.undercloud.Undercloud(
            hostname=dci_conf['undercloud_ip'],
            user='stack',
            key_filename=dci_conf['key_filename'])
        undercloud.run('sudo mkdir /root/.ssh', retry=600, user='stack')
        undercloud.run('sudo chmod 700 /root/.ssh', user='stack')
        undercloud.run('sudo cp /home/stack/.ssh/authorized_keys /root/.ssh/', user='stack')
        dci_jobstate.create(
            ctx,
            'running',
            'undercloud deployment',
            ctx.last_job_id)
        dci_helper.run_command(ctx, dci_conf['commands']['undercloud'], shell=True)
        dci_jobstate.create(ctx, 'running', 'overcloud deployment', ctx.last_job_id)
        dci_helper.run_command(ctx, dci_conf['commands']['overcloud'], shell=True)
        dci_tripleo_helper.run_tests(
            ctx,
            undercloud_ip='192.168.100.10',
            stack_name='lab2',
            key_filename=dci_conf['key_filename'])
    except Exception as e:
        dci_jobstate.create(ctx, 'failure', 'An exception occured.', ctx.last_job_id)
        content = traceback.format_exc()
        print(content)
        dci_file.create(ctx, 'error', str(e), mime='text/plain', jobstate_id=ctx.last_jobstate_id)
        dci_file.create(ctx, 'backtrace', content, mime='text/plain', jobstate_id=ctx.last_jobstate_id)

if __name__ == '__main__':
    main()
