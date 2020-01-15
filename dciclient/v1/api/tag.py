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

from dciclient.v1.api import base


RESOURCE = "tags"


def create(context, name):
    return base.create(context, RESOURCE, name=name)


def add_tag_to_resource(context, resource, id, name):
    uri = "%s/%s/%s/tags" % (context.dci_cs_api, resource, id)
    return context.session.post(uri, json={"name": name})


def list(context):
    return base.get(context, RESOURCE)


def delete_tag_from_resource(context, resource, id, tag_id):
    return base.delete(context, resource, id, subresource="tags", subresource_id=tag_id)


def delete(context, id):
    return base.delete(context, RESOURCE, id)
