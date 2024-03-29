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


from dciclient.v1.api import base


RESOURCE = "pipelines"

HTTP_TIMEOUT = 600


def create(context, name, team_id):
    return base.create(
        context,
        RESOURCE,
        name=name,
        team_id=team_id
    )


def get(context, id, **kwargs):
    return base.get(context, RESOURCE, id=id, **kwargs)


def list(context, **kwargs):
    return base.list(context, RESOURCE, **kwargs)


def update(context, id, **kwargs):
    return base.update(context, RESOURCE, id=id, **kwargs)


def get_jobs(context, id, **kwargs):
    uri = "%s/%s/%s/jobs" % (context.dci_cs_api, RESOURCE, id)
    return context.session.get(uri, timeout=HTTP_TIMEOUT, params=kwargs)


def delete(context, id, etag):
    return base.delete(context, RESOURCE, id=id, etag=etag)
