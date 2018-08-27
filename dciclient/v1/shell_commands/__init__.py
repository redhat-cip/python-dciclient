# -*- encoding: utf-8 -*-
#
# Copyright 2015-2016 Red Hat, Inc.
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

from click.core import Command
from click.decorators import _make_command
from dciclient.v1.api import context as dci_context

# NOTE(Gonéri): we now ignore the --id parameter, we need this until the
# transition is done.
import sys
sys.argv = [a for a in sys.argv if a != '--id']

click.disable_unicode_literals_warning = True
_default_dci_cs_url = 'http://127.0.0.1:5000'
_default_sso_url = 'http://127.0.0.1:8180'


# Override Click command so that to preserve the function's docstring,
# this is useful for sphinx autodoc generation
def command(name=None, cls=None, **attrs):
    if cls is None:
        cls = Command

    def decorator(f):
        r = _make_command(f, name, attrs, cls)
        r.__doc__ = f.__doc__
        return r
    return decorator

click.core.command = command


@click.group()
@click.option('--dci-login', envvar='DCI_LOGIN',
              help="DCI login or 'DCI_LOGIN' environment variable.")
@click.option('--dci-password', envvar='DCI_PASSWORD',
              help="DCI password or 'DCI_PASSWORD' environment variable.")
@click.option('--dci-client-id', envvar='DCI_CLIENT_ID',
              help="DCI login or 'DCI_LOGIN' environment variable.")
@click.option('--dci-api-secret', envvar='DCI_API_SECRET',
              help="DCI password or 'DCI_PASSWORD' environment variable.")
@click.option('--dci-cs-url', envvar='DCI_CS_URL', default=_default_dci_cs_url,
              help="DCI control server url, default to '%s'." %
                   _default_dci_cs_url)
@click.option('--sso-url', envvar='SSO_URL', default=_default_sso_url,
              help="SSO url, default to '%s'." % _default_sso_url)
@click.option('--sso-username', envvar='SSO_USERNAME',
              help="SSO username or 'SSO_USERNAME' environment variable.")
@click.option('--sso-password', envvar='SSO_PASSWORD',
              help="SSO password or 'SSO_PASSWORD' environment variable.")
@click.option('--sso-token', envvar='SSO_TOKEN',
              help="SSO token or 'SSO_TOKEN' environment variable.")
@click.option("--refresh-sso-token", required=False, default=False,
              is_flag=True, help="Refresh the token")
@click.option('--format', envvar='DCI_CLI_OUTPUT_FORMAT', required=False,
              default='table', help="DCI CLI output format.")
@click.pass_context
def cli(ctx, dci_login, dci_password, dci_client_id, dci_api_secret,
        dci_cs_url, sso_url, sso_username, sso_password, sso_token,
        refresh_sso_token, format):
    if dci_login is not None and dci_password is not None:
        context = dci_context.build_dci_context(dci_login=dci_login,
                                                dci_password=dci_password,
                                                dci_cs_url=dci_cs_url)
    elif ((sso_url is not None and sso_username is not None and
          sso_password is not None) or sso_token is not None):
        context = dci_context.build_sso_context(dci_cs_url, sso_url,
                                                sso_username, sso_password,
                                                sso_token,
                                                refresh=refresh_sso_token)
    elif dci_client_id is not None and dci_api_secret is not None:
        context = dci_context.build_signature_context(
            dci_cs_url=dci_cs_url,
            dci_client_id=dci_client_id,
            dci_api_secret=dci_api_secret
        )
    else:
        raise click.UsageError(
            'Missing options --dci-login and --dci-password or '
            '--dci-client-id and dci-api-secret.')

    context.format = format
    ctx.obj = context


import dciclient.v1.shell_commands.analytic  # noqa
import dciclient.v1.shell_commands.component  # noqa
import dciclient.v1.shell_commands.feeder  # noqa
import dciclient.v1.shell_commands.file  # noqa
import dciclient.v1.shell_commands.job  # noqa
import dciclient.v1.shell_commands.jobstate  # noqa
import dciclient.v1.shell_commands.product  # noqa
import dciclient.v1.shell_commands.purge  # noqa
import dciclient.v1.shell_commands.remoteci  # noqa
import dciclient.v1.shell_commands.role  # noqa
import dciclient.v1.shell_commands.team  # noqa
import dciclient.v1.shell_commands.test  # noqa
import dciclient.v1.shell_commands.topic  # noqa
import dciclient.v1.shell_commands.user  # noqa
