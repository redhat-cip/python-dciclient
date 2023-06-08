# -*- encoding: utf-8 -*-
#
# Copyright 2015-2021 Red Hat, Inc.
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

from dciclient.v1.api import base
from dciclient.v1 import utils
from dciclient.v1.api.tag import add_tag_to_resource, delete_tag_from_resource


RESOURCE = "jobs"


def create(context, topic_id, **kwargs):
    kwargs = utils.sanitize_kwargs(**kwargs)
    job = base.create(
        context,
        RESOURCE,
        topic_id=topic_id,
        **kwargs)
    if job.status_code == 201:
        context.last_job_id = job.json()["job"]["id"]
    return job


def update(context, **kwargs):
    return base.update(context, RESOURCE, **kwargs)


def list(context, **kwargs):
    return base.list(context, RESOURCE, **kwargs)


def schedule(context, topic_id, **kwargs):
    uri = "%s/%s/schedule" % (context.dci_cs_api, RESOURCE)
    data = {"topic_id": topic_id}
    data.update(kwargs)
    data = utils.sanitize_kwargs(**data)
    r = context.session.post(uri, json=data)
    if r.status_code == 201:
        context.last_job_id = r.json()["job"]["id"]
    return r


def job_update(context, job_id):
    uri = "%s/%s/%s/update" % (context.dci_cs_api, RESOURCE, job_id)
    r = context.session.post(uri)
    if r.status_code == 201:
        context.last_job_id = r.json()["job"]["id"]
    return r


def upgrade(context, job_id):
    uri = "%s/%s/upgrade" % (context.dci_cs_api, RESOURCE)
    data = {"job_id": job_id}
    r = context.session.post(uri, json=data)
    if r.status_code == 201:
        context.last_job_id = r.json()["job"]["id"]
    return r


def get(context, id, **kwargs):
    return base.get(context, RESOURCE, id=id, **kwargs)


def list_results(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id, subresource="results", **kwargs)


def iter(context, **kwargs):
    return base.iter(context, RESOURCE, **kwargs)


def add_component(context, job_id, component_id):
    uri = "%s/%s/%s/components" % (context.dci_cs_api, RESOURCE, job_id)
    data = {'id': component_id}
    return context.session.post(uri, json=data)


def get_components(context, id):
    uri = "%s/%s/%s/components" % (context.dci_cs_api, RESOURCE, id)
    return context.session.get(uri)


def delete(context, id, etag):
    return base.delete(context, RESOURCE, id=id, etag=etag)


def list_files(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id, subresource="files", **kwargs)


def list_files_iter(context, id, **kwargs):
    return base.iter(context, RESOURCE, id=id, subresource="files", **kwargs)


def list_jobstates(context, id, **kwargs):
    return base.list(context, RESOURCE, id=id, subresource="jobstates", **kwargs)


def list_tags(context, id):
    job = base.get(context, RESOURCE, id=id).json()["job"]
    tags = job["tags"]
    return {"tags": tags, "_meta": {"count": len(tags)}}


def add_tag(context, id, name):
    return add_tag_to_resource(context, RESOURCE, id, name)


def delete_tag(context, id, name):
    return delete_tag_from_resource(context, RESOURCE, id, name)
