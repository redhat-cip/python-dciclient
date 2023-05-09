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

from dciclient.v1.api import job
from dciclient.v1.api import file


def list(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "where"]}
    return job.list_files(context, id=args.job_id, **params)


def show(context, args):
    return file.content(context, id=args.id)


def delete(context, args):
    return file.delete(context, id=args.id)
