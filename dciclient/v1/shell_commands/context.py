#
# Copyright (C) 2022 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from dciclient.v1.api.context import (build_dci_context,
                                      build_signature_context,
                                      build_sso_context)


_default_dci_cs_url = "http://127.0.0.1:5000"
_default_sso_url = "http://127.0.0.1:8180"


def parse_auth_arguments(parser, environment={}):
    parser.add_argument(
        "--dci-login",
        default=environment.get("DCI_LOGIN", None),
        help="DCI login or 'DCI_LOGIN' environment variable.",
    )
    parser.add_argument(
        "--dci-password",
        default=environment.get("DCI_PASSWORD", None),
        help="DCI password or 'DCI_PASSWORD' environment variable.",
    )
    parser.add_argument(
        "--dci-client-id",
        default=environment.get("DCI_CLIENT_ID", None),
        help="DCI CLIENT ID or 'DCI_CLIENT_ID' environment variable.",
    )
    parser.add_argument(
        "--dci-api-secret",
        default=environment.get("DCI_API_SECRET", None),
        help="DCI API secret or 'DCI_API_SECRET' environment variable.",
    )
    parser.add_argument(
        "--dci-cs-url",
        default=environment.get("DCI_CS_URL", _default_dci_cs_url),
        help="DCI control server url, default to '%s'." % _default_dci_cs_url,
    )
    parser.add_argument(
        "--sso-url",
        default=environment.get("SSO_URL", _default_sso_url),
        help="SSO url, default to '%s'." % _default_sso_url,
    )
    parser.add_argument(
        "--sso-username",
        default=environment.get("SSO_USERNAME"),
        help="SSO username or 'SSO_USERNAME' environment variable.",
    )
    parser.add_argument(
        "--sso-password",
        default=environment.get("SSO_PASSWORD"),
        help="SSO password or 'SSO_PASSWORD' environment variable.",
    )
    parser.add_argument(
        "--sso-token",
        default=environment.get("SSO_TOKEN"),
        help="SSO token or 'SSO_TOKEN' environment variable.",
    )
    parser.add_argument(
        "--refresh-sso-token",
        default=False,
        action="store_true",
        help="Refresh the token",
    )
    parser.add_argument(
        "--format",
        default=environment.get("DCI_FORMAT", "table"),
        choices=["table", "json", "csv", "tsv"],
        help="Output format",
    )
    parser.add_argument(
        "--verbose", "--long",
        default=False,
        action="store_true",
        help="Display extra fields.",
    )


def build_context(args):
    if args.sso_token or (args.sso_url and args.sso_username and args.sso_password):
        context = build_sso_context(
            dci_cs_url=args.dci_cs_url,
            sso_url=args.sso_url,
            username=args.sso_username,
            password=args.sso_password,
            token=args.sso_token,
            refresh=args.refresh_sso_token,
        )
    elif args.dci_client_id and args.dci_api_secret:
        context = build_signature_context(
            dci_cs_url=args.dci_cs_url,
            dci_client_id=args.dci_client_id,
            dci_api_secret=args.dci_api_secret,
        )
    elif args.dci_login and args.dci_password:
        context = build_dci_context(
            dci_cs_url=args.dci_cs_url,
            dci_login=args.dci_login,
            dci_password=args.dci_password,
        )
    else:
        context = None

    return context
