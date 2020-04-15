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
from dciclient.v1.shell_commands import team
from dciclient.v1.shell_commands import topic
from dciclient.v1.shell_commands import component
from dciclient.v1.shell_commands import file


command_function = {
    "user-list": user.list,
    "user-create": user.create,
    "user-show": user.show,
    "user-update": user.update,
    "user-delete": user.delete,
    "team-list": team.list,
    "team-create": team.create,
    "team-show": team.show,
    "team-update": team.update,
    "team-delete": team.delete,
    "topic-list": topic.list,
    "topic-create": topic.create,
    "topic-show": topic.show,
    "topic-attach-team": topic.attach_team,
    "topic-unattach-team": topic.unattach_team,
    "topic-list-team": topic.list_team,
    "topic-update": topic.update,
    "topic-delete": topic.delete,
    "component-list": component.list,
    "component-create": component.create,
    "component-show": component.show,
    "component-attach-issue": component.attach_issue,
    "component-unattach-issue": component.unattach_issue,
    "component-list-issue": component.list_issues,
    "component-update": component.update,
    "component-delete": component.delete,
    "component-file-list": component.file_list,
    "component-file-upload": component.file_upload,
    "component-file-show": component.file_show,
    "component-file-download": component.file_download,
    "component-file-delete": component.file_delete,
    "file-list": file.list,
    "file-show": file.show,
    "file-delete": file.delete,
}


def run(context, args):
    return command_function[args.command](context, args)
