# -*- encoding: utf-8 -*-
#
# Copyright Red Hat, Inc.
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
from dciclient.v1.shell_commands import topic


command_columns = {
    "user-list": user.COLUMNS,
    "user-create": user.COLUMNS,
    "user-show": user.COLUMNS,
    "user-update": user.COLUMNS,
    "user-delete": user.COLUMNS,
    "topic-list": topic.COLUMNS,
    "topic-create": topic.COLUMNS,
    "topic-show": topic.COLUMNS,
    "topic-update": topic.COLUMNS,
    "topic-delete": topic.COLUMNS,
}


def get_columns(args):
    if args.command in command_columns:
        return command_columns[args.command]
    return None
