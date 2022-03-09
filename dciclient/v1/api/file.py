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
from dciclient.v1 import utils

import io
import os

RESOURCE = "files"


def create(
    context,
    name,
    content=None,
    file_path=None,
    mime="text/plain",
    jobstate_id=None,
    md5=None,
    job_id=None,
):
    """Method to create a file on the Control-Server

    This method allows one to upload a file to the Control-Server. The file
    to be uploaded can be specified in two different ways either by specifying
    its content directly or or by specifying the file_path where the file is
    located.

    content can be in the form of: string, bytes or a file-descriptor.

    """

    if content is not None and file_path:
        raise Exception("content and file_path are mutually exclusive")
    elif content is None and not file_path:
        raise Exception("At least one of content or file_path must be specified")

    headers = {
        "DCI-NAME": name,
        "DCI-MIME": mime,
        "DCI-JOBSTATE-ID": jobstate_id,
        "DCI-MD5": md5,
        "DCI-JOB-ID": job_id,
        "Content-Type": mime
    }
    headers = utils.sanitize_kwargs(**headers)
    uri = "%s/%s" % (context.dci_cs_api, RESOURCE)

    if content is not None:
        if not hasattr(content, "read"):
            if not isinstance(content, bytes):
                content = content.encode("utf-8")
            content = io.BytesIO(content)
        return context.session.post(uri, headers=headers, data=content)
    else:
        if not os.path.exists(file_path):
            raise FileErrorException()
        with open(file_path, "rb") as f:
            return context.session.post(uri, headers=headers, data=f)


# TODO(spredzy): Remove this method once all the party using this method has
#                moved to create()
def create_with_stream(
    context,
    name,
    file_path,
    mime="text/plain",
    jobstate_id=None,
    md5=None,
    job_id=None,
):
    return create(
        context,
        name,
        file_path=file_path,
        mime=mime,
        jobstate_id=jobstate_id,
        md5=md5,
        job_id=job_id,
    )


def get(context, id, **kwargs):
    return base.get(context, RESOURCE, id=id, **kwargs)


def list(context, **kwargs):
    return base.list(context, RESOURCE, **kwargs)


def iter(context, **kwargs):
    return base.iter(context, RESOURCE, **kwargs)


def delete(context, id):
    return base.delete(context, RESOURCE, id=id)


def content(context, id):
    uri = "%s/%s/%s/content" % (context.dci_cs_api, RESOURCE, id)
    r = context.session.get(uri)
    return r


def download(context, id, file_id, target):
    uri = "%s/files/%s/content" % (context.dci_cs_api, file_id)
    base.download(context, uri, target)


class FileErrorException(Exception):
    def __init__(self, *args, **kwargs):
        super(FileErrorException, self).__init__(self, *args, **kwargs)
