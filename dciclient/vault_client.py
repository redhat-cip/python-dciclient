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

'''DCI vault-id client for Ansible vault

Use the DCI_API_SECRET as a password for ansible-vault (stdout).
'''

import hashlib
import os
import sys
from argparse import ArgumentParser

from dciclient.version import __version__


def parse_arguments(args, environment={}):
    base_parser = ArgumentParser(add_help=False)
    base_parser.add_argument("--verbose", "--long", default=False, action="store_true")

    parser = ArgumentParser(prog="dci-vault-client")
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )
    parser.add_argument(
        "--dci-api-secret",
        default=environment.get("DCI_API_SECRET", None),
        help="DCI API secret or 'DCI_API_SECRET' environment variable.",
    )
    parser.add_argument(
        "--vault-id",
        default="",
        help="Ansible Vault id.",
    )

    args = parser.parse_args(args)

    return args


def main():
    args = parse_arguments(sys.argv[1:], os.environ)

    if args.dci_api_secret is None:
        sys.stderr.write("No DCI_API_SECRET set. Aborting.\n")
        sys.exit(1)

    password = hashlib.sha256((args.dci_api_secret +
                               args.vault_id).encode("utf-8")).hexdigest()

    print(password)
