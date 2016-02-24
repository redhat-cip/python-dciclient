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

import click
import requests
import yaml

import logging
import os
import sys
import traceback

from dciclient.v1.api import component
from dciclient.v1.api import context as dcicontext
from dciclient.v1.api import job as dcijob
from dciclient.v1.api import jobstate as dcijobstate
from dciclient.v1 import logger

from rdomhelper import logger as chainsaw_logger
from rdomhelper.provisioners.openstack import provisioner as os_provisioner


LOG = logging.getLogger('__chainsaw__')


def _check_url(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        LOG.error("url '%s' is not available, content '%s'" %
                  (url, resp.content))
        raise


def _get_job_puddles(dci_context, job_id, mirror_repo_url):
    """Get the repositories of the puddles to test from the control server.
    Returns the content of the .repo files.
    """
    job_details = dcijob.get_full_data(dci_context, job_id)
    job_puddles = []
    for job_component in job_details['components']:
        if job_component['type'] == component.PUDDLE:
            puddle_name = job_component['canonical_project_name'].lower()
            repo_name = job_component['data']['repo_name']
            baseurl = "%s%s" % (mirror_repo_url, job_component['data']['path'])
            _check_url(baseurl)
            content = "[%s]\n"\
                      "name=%s\n"\
                      "baseurl=%s\n"\
                      "gpgcheck=0\n"\
                      "enabled=1\n" % (repo_name, repo_name, baseurl)

            job_puddles.append(
                {'type': 'yum_repo',
                 'content': content,
                 'dest': '/etc/yum.repos.d/%s.repo' % puddle_name})
    return job_puddles


@click.command()
@click.option('--os-auth-url', envvar='OS_AUTH_URL', required=True,
              help="Keystone auth url.")
@click.option('--os-username', envvar='OS_USERNAME', required=True,
              help="Openstack username account.")
@click.option('--os-password', envvar='OS_PASSWORD', required=True,
              help="Openstack password account.")
@click.option('--os-tenant-name', envvar='OS_TENANT_NAME', required=True,
              help="Openstack tenant name.")
@click.option('--dci-login', envvar='DCI_LOGIN', required=True,
              help="DCI username account.")
@click.option('--dci-password', envvar='DCI_PASSWORD', required=True,
              help="DCI password account.")
@click.option('--dci-cs-url', envvar='DCI_CS_URL', required=True,
              help="DCI CS url.")
@click.option('--dci-remoteci-id', envvar='DCI_REMOTECI_ID', required=True,
              help="DCI remoteci id.")
@click.option('--config-file', required=True, type=click.File('rb'),
              help="Chainsaw path configuration file.")
def cli(os_auth_url, os_username, os_password, os_tenant_name, dci_login,
        dci_password, dci_cs_url, dci_remoteci_id, config_file):
    config = yaml.load(config_file)
    mirror_repo_url = config['mirror_repo_url']

    dci_context = dcicontext.build_dci_context(
        dci_cs_url,
        dci_login,
        dci_password)
    dci_log_handler = logger.DciHandler(dci_context)
    chainsaw_logger.setup_logging(extra_handlers=(dci_log_handler,))
    status = 'pre-run'
    job = dcijob.schedule(dci_context, dci_remoteci_id)
    if job.status_code == 412:
        LOG.info("No jobs available for run.")
        sys.exit(0)
    elif job.status_code >= 400:
        LOG.error(job.text)
        sys.exit(1)
    job = job.json()
    job_id = job['job']['id']
    job_puddles = _get_job_puddles(dci_context, job_id, mirror_repo_url)

    try:
        rhsm_login = config['rhsm']['login']
        rhsm_password = config['rhsm'].get('password',
                                           os.environ.get('RHN_PW'))
        pool_id = config['rhsm'].get('pool_id')
        dcijobstate.create(dci_context, status, 'Creating the host0',
                           job_id)
        host0 = os_provisioner.deploy_host0(os_auth_url, os_username,
                                            os_password, os_tenant_name,
                                            config['provisioner'],
                                            config['ssh']['private_key'])

        provisioner_repositories = config['provisioner']['repositories']
        provisioner_repositories.extend(job_puddles)
        host0.configure(rhsm_login, rhsm_password, pool_id,
                        repositories=provisioner_repositories)

        dcijobstate.create(dci_context, status, 'Creating the undercloud',
                           job_id)
        vm_undercloud = host0.build_undercloud(
            config['undercloud']['guest_image_path'],
            config['undercloud']['guest_image_checksum'],
            rhsm_login=rhsm_login,
            rhsm_password=rhsm_password)

        status = 'running'
        dcijobstate.create(dci_context, status,
                           'Installing the undercloud machine', job_id)
        undercloud_repositories = config['undercloud']['repositories']
        undercloud_repositories.extend(job_puddles)
        vm_undercloud.configure(undercloud_repositories)
        vm_undercloud.install(config['undercloud']['guest_image_path'],
                              config['undercloud']['guest_image_checksum'])

        dcijobstate.create(dci_context, status, 'Deploying the overcloud',
                           job_id)
        vm_undercloud.deploy_overcloud(config['undercloud'].get('files', []))
        dcijobstate.create(dci_context, status, 'Running tempest', job_id)
        vm_undercloud.run_tempest()
        dcijobstate.create(dci_context, 'success', 'Job succeed :-)', job_id)
    except Exception as e:
        LOG.error(traceback.format_exc())
        dcijobstate.create(dci_context, 'failure', 'Job failed :-(', job_id)
        raise e

if __name__ == '__main__':
    cli()
