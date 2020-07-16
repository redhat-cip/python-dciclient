# -*- encoding: utf-8 -*-
#
# Copyright 2015-2016 Red Hat, Inc.
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


RESOURCE = "users"


def create(context, name, password, email, fullname, state="active"):
    return base.create(
        context,
        RESOURCE,
        name=name,
        password=password,
        state=state,
        email=email,
        fullname=fullname,
    )


def list(context, **kwargs):
    return base.list(context, RESOURCE, **kwargs)


def get(context, id, **kwargs):
    return base.get(context, RESOURCE, id=id, **kwargs)


def get_current_user(context):
    uri = "%s/%s/me" % (context.dci_cs_api, RESOURCE)
    return context.session.get(uri)


def update(
    context,
    id,
    etag,
    name=None,
    password=None,
    team_id=None,
    state=None,
    email=None,
    fullname=None,
):
    return base.update(
        context,
        RESOURCE,
        id=id,
        etag=etag,
        name=name,
        password=password,
        state=state,
        email=email,
        fullname=fullname,
    )


def delete(context, id, etag):
    return base.delete(context, RESOURCE, id=id, etag=etag)
