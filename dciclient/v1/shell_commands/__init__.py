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

from dciclient.v1.shell_commands.core import DciCtl


cli = DciCtl()
import dciclient.v1.shell_commands.user
import dciclient.v1.shell_commands.topic
import dciclient.v1.shell_commands.test
import dciclient.v1.shell_commands.team
import dciclient.v1.shell_commands.tag
import dciclient.v1.shell_commands.remoteci
import dciclient.v1.shell_commands.purge
import dciclient.v1.shell_commands.product
import dciclient.v1.shell_commands.job
import dciclient.v1.shell_commands.jobstate
import dciclient.v1.shell_commands.file
import dciclient.v1.shell_commands.feeder
import dciclient.v1.shell_commands.component
import dciclient.v1.shell_commands.analytic
