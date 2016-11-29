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

from datetime import datetime
import hashlib
import hmac

from dciclient.v1.exceptions import ClientError


def format_for_signature(http_verb, content_type, timestamp, url,
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


def is_clientid_valid(client_id):
    type, sep, rss_id = client_id.partition('/')
    if not type or not sep or not rss_id or sep != '/':
        return False
    return True


def gen_signature(secret, http_verb, content_type, timestamp, url,
                  query_string, payload):
    """Generates a signature compatible with DCI for the parameters passed"""
    payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    stringtosign = format_for_signature(
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


def gen_headers(client_id, secret, http_verb, content_type, url,
                query_string, payload):
    if not is_clientid_valid(client_id):
        raise ClientError('The supplied client_id is invalid. '
                          'It should match "<type>/<uuid>".')

    timestamp = datetime.utcnow()
    client_id = '%s/%s' % (timestamp.strftime('%Y-%m-%d %H:%M:%SZ'),
                           client_id)
    signature = gen_signature(secret, http_verb, content_type, timestamp,
                              url, query_string, payload)

    return {
        'DCI-Client-ID': client_id,
        'DCI-Auth-Signature': signature,
    }
