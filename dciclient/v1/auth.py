# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import hashlib
import hmac
import os


def _hash_file(fd):
    algo = hashlib.sha256()
    block_size = 1024 * 1024
    buf = fd.read(block_size)
    while len(buf) > 0:
        algo.update(buf)
        buf = fd.read(block_size)
    return algo.hexdigest()


def _get_payload_hash(payload):
    if hasattr(payload, 'read'):
        payload_hash = _hash_file(payload)
        payload.seek(0, os.SEEK_SET)
    else:
        payload_hash = hashlib.sha256(payload).hexdigest()
    return payload_hash


def string_to_sign(http_verb, content_type, timestamp, url,
                   query_string, payload_hash):
    """Returns the string used to generate the signature in a correctly
    formatter manner.
    """
    return '\n'.join((http_verb,
                      content_type,
                      timestamp.strftime('%Y-%m-%d %H:%M:%SZ'),
                      url,
                      query_string,
                      payload_hash))


def sign(secret, http_verb, content_type, timestamp, url,
         query_string, payload):
    """Generates a signature compatible with DCI for the parameters passed"""
    if payload is None:
        payload = b""

    payload_hash = _get_payload_hash(payload)

    stringtosign = string_to_sign(
        http_verb,
        content_type,
        timestamp,
        url,
        query_string,
        payload_hash
    )

    return hmac.new(secret.encode('utf-8'),
                    stringtosign.encode('utf-8'),
                    hashlib.sha256).hexdigest()
