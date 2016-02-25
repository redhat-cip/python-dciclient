# -*- encoding: utf-8 -*-
#
# Copyright 2015 Red Hat, Inc.
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

import logging
import time

from dciclient.v1.api import jobstate
import dciclient.v1.logger

import pytest


def test_logger_no_context(dci_context):
    my_logger = logging.getLogger('__chainsaw__')
    handler = dciclient.v1.logger.DciHandler(dci_context)
    my_logger.addHandler(handler)
    my_logger.info('bob')
    with pytest.raises(dciclient.v1.logger.DciLoggerContextError):
        handler._send_log_file()


def test_logger_server_outage(monkeypatch, dci_context, dci_context_broken):
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    my_logger = logging.getLogger('__chainsaw__')
    handler = dciclient.v1.logger.DciHandler(dci_context_broken)
    my_logger.addHandler(handler)
    my_logger.info('bob')
    print(dci_context)
    with pytest.raises(dciclient.v1.logger.DciLoggerPushError):
        handler._send_log_file()


def test_logger_server(dci_context, job_id):
    jobstate.create(dci_context, 'pre-run', 'comment', job_id)
    my_logger = logging.getLogger('__chainsaw__')
    handler = dciclient.v1.logger.DciHandler(dci_context)
    my_logger.addHandler(handler)
    my_logger.info('bob')
    handler._send_log_file()


def test_logger_info_as_jobstate(dci_context, job_id):
    my_logger = logging.getLogger('__chainsaw__')
    handler = dciclient.v1.logger.DciHandler(
        dci_context, info_as_jobstate=True)
    my_logger.addHandler(handler)
    my_logger.info('bob')
    handler.emit(None)
