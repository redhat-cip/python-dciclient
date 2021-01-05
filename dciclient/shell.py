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
import os
import sys
from dciclient.v1.shell_commands.cli import parse_arguments
from dciclient.v1.shell_commands import columns
from dciclient.v1.api import context as dci_context
from dciclient.v1.shell_commands.runner import run
from dciclient.printer import print_response


def main():
    args = parse_arguments(sys.argv[1:], os.environ)
    dci_cs_url = args.dci_cs_url
    dci_login = args.dci_login
    dci_password = args.dci_password
    context = None
    if dci_login is not None and dci_password is not None:
        context = dci_context.build_dci_context(
            dci_login=dci_login, dci_password=dci_password, dci_cs_url=dci_cs_url
        )
    sso_url = args.sso_url
    sso_username = args.sso_username
    sso_password = args.sso_password
    sso_token = args.sso_token
    refresh_sso_token = args.refresh_sso_token
    if (
        sso_url is not None and sso_username is not None and sso_password is not None
    ) or sso_token is not None:
        context = dci_context.build_sso_context(
            dci_cs_url,
            sso_url,
            sso_username,
            sso_password,
            sso_token,
            refresh=refresh_sso_token,
        )
    dci_client_id = args.dci_client_id
    dci_api_secret = args.dci_api_secret
    if dci_client_id is not None and dci_api_secret is not None:
        context = dci_context.build_signature_context(
            dci_cs_url=dci_cs_url,
            dci_client_id=dci_client_id,
            dci_api_secret=dci_api_secret,
        )
    if not context:
        print("No credentials provided.")
        sys.exit(1)
    response = run(context, args)
    _columns = columns.get_columns(args)
    print_response(response, args.format, args.verbose, _columns)
