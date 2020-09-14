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


def add_tag_to_resource(context, resource_name, id, tag_name):
    r = base.get(context, resource_name, id=id)
    resource_name_singular = resource_name[:-1]
    resource = r.json()[resource_name_singular]
    tags = resource["tags"]
    if tag_name not in tags:
        tags.append(tag_name)
    return base.update(context, resource_name, id=id, etag=resource["etag"], tags=tags)


def delete_tag_from_resource(context, resource_name, id, tag_name):
    r = base.get(context, resource_name, id=id)
    resource_name_singular = resource_name[:-1]
    resource = r.json()[resource_name_singular]
    tags = resource["tags"]
    if tag_name in tags:
        tags.remove(tag_name)
    return base.update(context, resource_name, id=id, etag=resource["etag"], tags=tags)
