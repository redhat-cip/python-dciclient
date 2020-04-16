# -*- encoding: utf-8 -*-
#
# Copyright Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from dciclient.v1.api import analytic


def list(context, args):
    return analytic.list(context, job_id=args.job_id)


def create(context, args):
    params = {k: getattr(args, k) for k in ["job_id", "name", "type", "url", "data"]}
    return analytic.create(context, **params)


def show(context, args):
    return analytic.get(context, id=args.id, job_id=args.job_id)


def update(context, args):
    params = {
        k: getattr(args, k)
        for k in ["id", "etag", "job_id", "name", "type", "url", "data"]
    }
    return analytic.update(context, **params)
