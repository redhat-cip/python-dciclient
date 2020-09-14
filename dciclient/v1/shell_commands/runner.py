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
from dciclient.v1.shell_commands import analytic
from dciclient.v1.shell_commands import user
from dciclient.v1.shell_commands import team
from dciclient.v1.shell_commands import product
from dciclient.v1.shell_commands import feeder
from dciclient.v1.shell_commands import jobstate
from dciclient.v1.shell_commands import topic
from dciclient.v1.shell_commands import component
from dciclient.v1.shell_commands import file
from dciclient.v1.shell_commands import job
from dciclient.v1.shell_commands import test
from dciclient.v1.shell_commands import remoteci
from dciclient.v1.shell_commands import purge


command_function = {
    "analytic-list": analytic.list,
    "analytic-create": analytic.create,
    "analytic-show": analytic.show,
    "analytic-update": analytic.update,
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
    "product-list": product.list,
    "product-create": product.create,
    "product-show": product.show,
    "product-update": product.update,
    "product-delete": product.delete,
    "product-attach-team": product.attach_team,
    "product-detach-team": product.detach_team,
    "product-list-teams": product.list_teams,
    "feeder-list": feeder.list,
    "feeder-create": feeder.create,
    "feeder-show": feeder.show,
    "feeder-update": feeder.update,
    "feeder-delete": feeder.delete,
    "feeder-reset-api-secret": feeder.reset_api_secret,
    "jobstate-show": jobstate.show,
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
    "job-list": job.list,
    "job-show": job.show,
    "job-delete": job.delete,
    "job-results": job.list_results,
    "job-attach-issue": job.attach_issue,
    "job-unattach-issue": job.unattach_issue,
    "job-list-issue": job.list_issues,
    "job-output": job.output,
    "job-list-test": job.list_tests,
    "job-upload-file": job.file_upload,
    "job-download-file": job.file_download,
    "job-show-file": job.file_show,
    "job-list-file": job.file_list,
    "job-delete-file": job.file_delete,
    "test-list": test.list,
    "test-create": test.create,
    "test-update": test.update,
    "test-delete": test.delete,
    "test-show": test.show,
    "remoteci-list": remoteci.list,
    "remoteci-create": remoteci.create,
    "remoteci-update": remoteci.update,
    "remoteci-delete": remoteci.delete,
    "remoteci-show": remoteci.show,
    "remoteci-get-data": remoteci.get_data,
    "remoteci-attach-test": remoteci.attach_test,
    "remoteci-unattach-test": remoteci.unattach_test,
    "remoteci-list-test": remoteci.list_test,
    "remoteci-attach-user": remoteci.attach_user,
    "remoteci-unattach-user": remoteci.unattach_user,
    "remoteci-list-user": remoteci.list_user,
    "remoteci-reset-api-secret": remoteci.reset_api_secret,
    "remoteci-refresh-keys": remoteci.refresh_keys,
    "purge": purge.purge,
}


def run(context, args):
    return command_function[args.command](context, args)
