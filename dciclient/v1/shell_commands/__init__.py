# -*- encoding: utf-8 -*-
#
# Copyright 2015 Red Hat, Inc.
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

import click
import requests


_default_dci_cs_url = 'http://127.0.0.1:5000'


def _get_http_session(dci_cs_url, login, password):
    session = requests.Session()
    session.headers.setdefault('Content-Type', 'application/json')
    session.auth = (login, password)
    session.dci_cs_url = dci_cs_url
    return session


@click.group()
@click.option('--dci-login', envvar='DCI_LOGIN', required=True,
              help="DCI login or 'DCI_LOGIN' environment variable.")
@click.option('--dci-password', envvar='DCI_PASSWORD', required=True,
              help="DCI password or 'DCI_PASSWORD' environment variable.")
@click.option('--dci-cs-url', envvar='DCI_CS_URL', default=_default_dci_cs_url,
              help="DCI control server url, default to '%s'." %
                   _default_dci_cs_url)
@click.pass_context
def cli(ctx, dci_login, dci_password, dci_cs_url):
    ctx.obj = _get_http_session(dci_cs_url, dci_login, dci_password)

import dciclient.v1.shell_commands.component  # noqa
