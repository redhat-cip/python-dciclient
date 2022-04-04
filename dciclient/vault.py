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

'''Wrapper on top of ansible-vault

Edit the command line arguments to replace --vault-id <name> with
--vault-id <name>@dci-vault-client.  If no --vault-id argument is
passed, add --vault-id dci-vault-client argument at the end.  Then
call ansible-vault with the modified arguments.
'''

import os
import sys


def replace_vault_id(vault_id, args):
    found = False
    ret = []
    for arg in args:
        if found:
            ret.append("%s@%s" % (arg, vault_id))
        else:
            ret.append(arg)
        found = (arg == "--vault-id")
    return ret


def main(args=sys.argv):
    prog_name = args[0]
    base_dir = os.path.dirname(prog_name)
    vault_client = os.path.join(base_dir, "dci-vault-client")
    new_args = replace_vault_id(vault_client, args)
    if "--vault_id" not in new_args:
        new_args.append("--vault-id")
        new_args.append(vault_client)
    new_args[0] = "ansible-vault"
    os.execvp("ansible-vault", new_args)
