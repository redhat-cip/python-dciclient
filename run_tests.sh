#!/usr/bin/env sh
#
# Copyright (C) 2017 Red Hat, Inc.
#
# Author: Dimitri Savineau <dsavinea@redhat.com>
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

set -x -e

# if the database is already running we do not want to run this script
if [ -z "$DISABLE_DB_START" ]; then
    pifpaf run postgresql -- py.test -v --cov-report html --cov dciclient $*
else
    PIFPAF_POSTGRESQL_URL='' py.test -v --cov-report html --cov dciclient $*
fi