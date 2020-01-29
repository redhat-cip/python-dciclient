#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the 'License'); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import datetime
import hashlib
import hmac


class Signature(object):
    def __init__(self, request, now=None):
        """
        dciauth Signature object implementing AWS HMAC version 4 mechanism.

        :param request (AuthRequest): dciauth AuthRequest object
        :param now (datetime): datetime used in Signature algorithm (default: datetime.utcnow())
        """

        self.request = request
        self.now = now or datetime.datetime.utcnow()
        self.dci_date_format = '%Y%m%d'
        self.dci_date_str = self.now.strftime(self.dci_date_format)
        self.dci_datetime_format = '%Y%m%dT%H%M%SZ'
        self.dci_datetime_str = self.now.strftime(self.dci_datetime_format)
        self.dci_datetime_header = 'dci-datetime'

    def generate_headers(self, client_type, client_id, secret):
        """
        generate_headers is used to generate the headers automatically for your http request

        :param client_type (str): remoteci or feeder
        :param client_id (str): remoteci or feeder id
        :param secret (str): api secret
        :return: Authorization headers (dict)
        """

        self.request.add_header(self.dci_datetime_header, self.dci_datetime_str)
        signature = self._sign(secret)
        return self.request.build_headers(client_type, client_id, signature)

    def is_valid(self, secret):
        dci_datetime_str = self.request.headers[self.dci_datetime_header]
        self._update_dci_dates(dci_datetime_str)
        signature = self._sign(secret)
        client_signature = self.request.get_client_info()['signature']
        return self._equals(signature, client_signature)

    def is_expired(self, hours=24):
        timestamp = self.request.headers.get(self.dci_datetime_header)
        if timestamp:
            timestamp = datetime.datetime.strptime(timestamp, self.dci_datetime_format)
            return abs(self.now - timestamp) > datetime.timedelta(hours=hours)
        return False

    def _create_canonical_request(self):
        payload_hash = hashlib.sha256(self.request.get_payload_string().encode('utf-8')).hexdigest()
        return """{method}
{endpoint}
{query_string}
{headers_string}
{signed_headers}
{payload_hash}""".format(method=self.request.method,
                         endpoint=self.request.endpoint,
                         query_string=self.request.get_query_string(),
                         headers_string=self.request.get_headers_string(),
                         signed_headers=self.request.get_signed_headers_string(),
                         payload_hash=payload_hash)

    def _create_string_to_sign(self):
        canonical_request = self._create_canonical_request()
        canonical_request_hash = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        return """{dci_algorithm}
{dci_datetime}
{dci_date}
{canonical_request_hash}""".format(dci_algorithm=self.request.algorithm,
                                   dci_datetime=self.dci_datetime_str,
                                   dci_date=self.dci_date_str,
                                   canonical_request_hash=canonical_request_hash)

    def _sign(self, secret):
        string_to_sign = self._create_string_to_sign()
        signing_key = hmac.new(
            secret.encode('utf-8'),
            self.dci_date_str.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    @staticmethod
    def _equals(client_signature, header_signature):
        return hmac.compare_digest(
            client_signature.encode('utf-8'),
            header_signature.encode('utf-8')
        )

    def _update_dci_dates(self, dci_datetime_str):
        dci_datetime = datetime.datetime.strptime(dci_datetime_str, self.dci_datetime_format)
        self.dci_date_str = dci_datetime.strftime(self.dci_date_format)
        self.dci_datetime_str = dci_datetime.strftime(self.dci_datetime_format)
