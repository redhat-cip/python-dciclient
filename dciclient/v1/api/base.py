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

from dciclient.v1 import utils

import os

HTTP_TIMEOUT = 600


def create(context, resource, **kwargs):
    """Create a resource"""
    data = utils.sanitize_kwargs(**kwargs)
    uri = "%s/%s" % (context.dci_cs_api, resource)
    r = context.session.post(uri, timeout=HTTP_TIMEOUT, json=data)
    return r


def get_or_create(context, resource, defaults, **kwargs):
    """Get or Create a resource with defaults"""
    data = utils.sanitize_kwargs(**kwargs)
    id = data.pop("id", None)
    subresource = data.pop("subresource", None)
    if subresource:
        uri = "%s/%s/%s/%s" % (context.dci_cs_api, resource, id, subresource)
    else:
        uri = "%s/%s" % (context.dci_cs_api, resource)
    params = {"where": ",".join(["%s:%s" % (k, v) for k, v in data.items()])}
    r = context.session.get(uri, timeout=HTTP_TIMEOUT, params=params)
    resource = subresource if subresource else resource
    items = r.json()[resource]
    if items:
        return get(context, resource, id=items[0]["id"], **data), False
    data = dict(data, **defaults)
    return create(context, resource, **data), True


def list(context, resource, **kwargs):
    """List all resources"""
    data = utils.sanitize_kwargs(**kwargs)
    id = data.pop("id", None)
    subresource = data.pop("subresource", None)

    if subresource:
        uri = "%s/%s/%s/%s" % (context.dci_cs_api, resource, id, subresource)
    else:
        uri = "%s/%s" % (context.dci_cs_api, resource)

    return context.session.get(uri, timeout=HTTP_TIMEOUT, params=data)


def iter(context, resource, **kwargs):
    """List all resources"""
    data = utils.sanitize_kwargs(**kwargs)
    id = data.pop("id", None)
    subresource = data.pop("subresource", None)
    data["limit"] = data.get("limit", 20)

    if subresource:
        uri = "%s/%s/%s/%s" % (context.dci_cs_api, resource, id, subresource)
        resource = subresource
    else:
        uri = "%s/%s" % (context.dci_cs_api, resource)

    data["offset"] = 0
    while True:
        j = context.session.get(uri, timeout=HTTP_TIMEOUT, params=data).json()
        if len(j[resource]):
            for i in j[resource]:
                yield i
        else:
            break
        data["offset"] += data["limit"]


def get(context, resource, **kwargs):
    """List a specific resource"""
    uri = "%s/%s/%s" % (context.dci_cs_api, resource, kwargs.pop("id"))
    r = context.session.get(uri, timeout=HTTP_TIMEOUT, params=kwargs)
    return r


def get_data(context, resource, **kwargs):
    """Retrieve data field from a resource"""

    url_suffix = ""
    if "keys" in kwargs and kwargs["keys"]:
        url_suffix = "/?keys=%s" % ",".join(kwargs.pop("keys"))

    uri = "%s/%s/%s/data%s" % (
        context.dci_cs_api,
        resource,
        kwargs.pop("id"),
        url_suffix,
    )

    r = context.session.get(uri, timeout=HTTP_TIMEOUT, params=kwargs)
    return r


def update(context, resource, **kwargs):
    """Update a specific resource"""
    etag = kwargs.pop("etag")
    id = kwargs.pop("id")
    data = utils.sanitize_kwargs(**kwargs)
    uri = "%s/%s/%s" % (context.dci_cs_api, resource, id)
    r = context.session.put(
        uri, timeout=HTTP_TIMEOUT, headers={"If-match": etag}, json=data
    )
    return r


def delete(context, resource, id, **kwargs):
    """Delete a specific resource"""

    etag = kwargs.pop("etag", None)
    id = id
    subresource = kwargs.pop("subresource", None)
    subresource_id = kwargs.pop("subresource_id", None)
    json = kwargs.pop("json", None)

    origin_uri = "%s/%s/%s" % (context.dci_cs_api, resource, id)
    uri = origin_uri
    if subresource is not None:
        uri = "%s/%s" % (origin_uri, subresource)
    if subresource is not None and subresource_id is not None:
        uri = "%s/%s/%s" % (origin_uri, subresource, subresource_id)

    r = context.session.delete(uri, timeout=HTTP_TIMEOUT, headers={"If-match": etag}, json=json)  # noqa
    return r


def purge(context, resource, **kwargs):
    """Purge resource type."""
    uri = "%s/%s/purge" % (context.dci_cs_api, resource)
    if "force" in kwargs and kwargs["force"]:
        r = context.session.post(uri, timeout=HTTP_TIMEOUT)
    else:
        r = context.session.get(uri, timeout=HTTP_TIMEOUT)
    return r


def download(context, uri, target):
    r = context.session.get(uri, stream=True, timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    with open(target + ".part", "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    os.rename(target + ".part", target)
    return r
