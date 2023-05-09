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

from dciclient.v1.api import pipeline


RESOURCE = "pipelines"

HTTP_TIMEOUT = 600


def create(context, args):
    return pipeline.create(context, args.name, args.team_id)


def show(context, args):
    return pipeline.get(context, args.id)


def list(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "where"]}
    return pipeline.list(context, **params)


def update(context, args):
    params = {
        k: getattr(args, k)
        for k in [
            "name",
            "state",
            "etag"
        ]
    }
    return pipeline.update(context, args.id, **params)


def get_jobs(context, args):
    uri = "%s/%s/%s/jobs" % (context.dci_cs_api, RESOURCE, args.id)
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset"]}
    return context.session.get(uri, timeout=HTTP_TIMEOUT, params=params)


def delete(context, args):
    return pipeline.delete(context, id=args.id, etag=args.etag)
