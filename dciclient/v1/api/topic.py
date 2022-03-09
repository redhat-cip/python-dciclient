# -*- encoding: utf-8 -*-
#
# Copyright 2016 Red Hat, Inc.
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


RESOURCE = "topics"


def create(
    context,
    name,
    component_types,
    state="active",
    product_id=None,
    next_topic_id=None,
    next_topic=None,
    data=None,
    export_control=False,
):
    return base.create(
        context,
        RESOURCE,
        name=name,
        state=state,
        component_types=component_types,
        product_id=product_id,
        next_topic_id=next_topic_id,
        next_topic=next_topic,
        data=data,
        export_control=export_control,
    )


def get_or_create(context, **kwargs):
    return base.get_or_create(context, RESOURCE, **kwargs)


def list(context, **kwargs):
    return base.list(context, RESOURCE, **kwargs)


def get(context, id, **kwargs):
    return base.get(context, RESOURCE, id=id, **kwargs)


def update(
    context,
    id,
    etag,
    name=None,
    component_types=None,
    next_topic_id=None,
    next_topic=None,
    state=None,
    product_id=None,
    data=None,
    export_control=None,
):
    return base.update(
        context,
        RESOURCE,
        id=id,
        etag=etag,
        name=name,
        component_types=component_types,
        next_topic_id=next_topic_id,
        state=state,
        product_id=product_id,
        next_topic=next_topic,
        data=data,
        export_control=export_control,
    )


def delete(context, id, etag):
    return base.delete(context, RESOURCE, id=id, etag=etag)


def attach_team(context, id, team_id):
    uri = "%s/%s/%s/teams" % (context.dci_cs_api, RESOURCE, id)
    return context.session.post(uri, json={"team_id": team_id})


def unattach_team(context, id, team_id):
    return base.delete(
        context, RESOURCE, id, subresource="teams", subresource_id=team_id
    )


def list_teams(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id, subresource="teams", **kwargs)


def list_components(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id, subresource="components", **kwargs)


def get_jobs_from_components(context, id, component_id, **kwargs):
    uri = "%s/%s/%s/components/%s/jobs" % (
        context.dci_cs_api,
        RESOURCE,
        id,
        component_id,
    )
    return context.session.get(uri, **kwargs)
