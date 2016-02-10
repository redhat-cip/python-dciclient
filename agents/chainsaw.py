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
import yaml

import logging
import os
import traceback

from dciclient.v1.api import context as dcicontext
from dciclient.v1.api import job as dcijob
from dciclient.v1.api import jobstate as dcijobstate

import rdomhelper.host0
from rdomhelper import logger
from rdomhelper.provisioners.openstack import provisioner as os_provisioner
from rdomhelper import undercloud


LOG = logging.getLogger('__chainsaw__')


@click.command()
@click.option('--os-auth-url', envvar='OS_AUTH_URL', required=True,
              help="Keystone auth url.")
@click.option('--os-username', envvar='OS_USERNAME', required=True,
              help="Openstack username account.")
@click.option('--os-password', envvar='OS_PASSWORD', required=True,
              help="Openstack password account.")
@click.option('--os-tenant-name', envvar='OS_TENANT_NAME', required=True,
              help="Openstack tenant name.")
@click.option('--host0-ip', required=False,
              help="IP address of a host0 to reuse.")
@click.option('--undercloud-ip', required=False,
              help="IP address of an undercloud to reuse.")
@click.option('--config-file', required=True, type=click.File('rb'),
              help="Chainsaw path configuration file.")
def cli(os_auth_url, os_username, os_password, os_tenant_name, host0_ip, undercloud_ip, config_file):
    config = yaml.load(config_file)
    ssh = config['ssh']
    host0 = None
    vm_undercloud = None

    dci_context = dcicontext.build_dci_context(
        config['dci']['control_server_url'],
        config['dci']['login'],
        config['dci']['password'])


    status = 'pre-run'
    job = dcijob.schedule(dci_context,
                          remoteci_id=config['dci']['remoteci_id']).json()
    job_id = job['job']['id']

    try:
        rhsm_login = config['rhsm']['login']
        rhsm_password = config['rhsm'].get('password', os.environ.get('RHN_PW'))
        pool_id = config['rhsm'].get('pool_id')
        if host0_ip:
            dcijobstate.create(dci_context, status, 'Reusing existing host0', job_id)
            host0 = rdomhelper.host0.Host0(hostname=host0_ip,
                                           user=config['provisioner']['image'].get('user', 'root'),
                                           key_filename=ssh['private_key'])
        else:
            dcijobstate.create(dci_context, status, 'Creating the host0', job_id)
            host0 = os_provisioner.deploy_host0(os_auth_url, os_username,
                                                os_password, os_tenant_name,
                                                config['provisioner'],
                                                config['ssh']['private_key'])
        host0.configure(rhsm_login, rhsm_password, pool_id,
                        repositories=config['provisioner']['repositories'])

        if undercloud_ip:
            dcijobstate.create(dci_context, status, 'Reusing existing undercloud', job_id)
            vm_undercloud = undercloud.Undercloud(hostname=undercloud_ip,
                                                  user='root',
                                                  via_ip=host0_ip,
                                                  key_filename=ssh['private_key'])
        else:
            dcijobstate.create(dci_context, status, 'Creating the undercloud', job_id)
            vm_undercloud = host0.build_undercloud(
                config['undercloud']['guest_image_path'],
                config['undercloud']['guest_image_checksum'],
                rhsm_login=rhsm_login,
                rhsm_password=rhsm_password)

        status = 'running'
        dcijobstate.create(dci_context, status, 'Installing the undercloud machine', job_id)
        vm_undercloud.configure(config['undercloud']['repositories'])
        vm_undercloud.install(config['undercloud']['guest_image_path'],
                              config['undercloud']['guest_image_checksum'])

        dcijobstate.create(dci_context, status, 'Deploying the overcloud', job_id)
        vm_undercloud.deploy_overcloud(config['undercloud'].get('files', []))
        dcijobstate.create(dci_context, status, 'Running tempest', job_id)
        vm_undercloud.run_tempest()
        dcijobstate.create(dci_context, 'success', 'Job succeed :-)', job_id)
    except Exception as e:
        if host0:
            LOG.info('___________')
            cmd = 'You can start from you current possition with the following command: '
            cmd += 'chainsaw --config-file %s --host0-ip %s' % (config_file.name, host0.hostname)
            if vm_undercloud:
                cmd += ' --undercloud-ip %s' % vm_undercloud.hostname
            LOG.info(cmd)
            LOG.info('___________')
        LOG.error(traceback.format_exc())
        dcijobstate.create(dci_context, 'failure', 'Job failed :-(', job_id)
        raise e

if __name__ == '__main__':
    cli()
