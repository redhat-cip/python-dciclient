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

from dciclient.v1.shell_commands import user
from dciclient.v1.shell_commands import feeder


command_function = {
    "user-list": user.list,
    "user-create": user.create,
    "user-show": user.show,
    "user-update": user.update,
    "user-delete": user.delete,
    "feeder-list": feeder.list,
    "feeder-create": feeder.create,
    "feeder-show": feeder.show,
    "feeder-update": feeder.update,
    "feeder-delete": feeder.delete,
    "feeder-reset-api-secret": feeder.reset_api_secret,
}


def run(context, args):
    return command_function[args.command](context, args)
