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

from dciclient.v1.api import context as dci_context


click.disable_unicode_literals_warning = True
_default_dci_cs_url = 'http://127.0.0.1:5000'


from click.core import Command
from click.decorators import _make_command


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
@click.option('--dci-login', envvar='DCI_LOGIN', required=True,
              help="DCI login or 'DCI_LOGIN' environment variable.")
@click.option('--dci-password', envvar='DCI_PASSWORD', required=True,
              help="DCI password or 'DCI_PASSWORD' environment variable.")
@click.option('--dci-cs-url', envvar='DCI_CS_URL', default=_default_dci_cs_url,
              help="DCI control server url, default to '%s'." %
                   _default_dci_cs_url)
@click.option('--format', envvar='DCI_CLI_OUTPUT_FORMAT', required=False,
              default='table', help="DCI CLI output format.")
@click.pass_context
def cli(ctx, dci_login, dci_password, dci_cs_url, format):
    context = dci_context.build_dci_context(dci_login=dci_login,
                                            dci_password=dci_password,
                                            dci_cs_url=dci_cs_url)
    context.format = format
    ctx.obj = context

import dciclient.v1.shell_commands.component  # noqa
import dciclient.v1.shell_commands.file  # noqa
import dciclient.v1.shell_commands.job  # noqa
import dciclient.v1.shell_commands.jobdefinition  # noqa
import dciclient.v1.shell_commands.jobstate  # noqa
import dciclient.v1.shell_commands.remoteci  # noqa
import dciclient.v1.shell_commands.team  # noqa
import dciclient.v1.shell_commands.test  # noqa
import dciclient.v1.shell_commands.topic  # noqa
import dciclient.v1.shell_commands.user  # noqa
