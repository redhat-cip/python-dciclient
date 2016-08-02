# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Red Hat, Inc
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

import functools
import io
import logging
import threading

from dciclient.v1.api import file as dci_file
from dciclient.v1.api import jobstate as dci_jobstate


class DciHandler(logging.Handler):
    def __init__(self, dci_context, info_as_jobstate=False, interval=30):
        logging.Handler.__init__(self)
        self._info_as_jobstate = info_as_jobstate
        self._dci_context = dci_context
        self._current_log = io.StringIO()
        self._threshold_log = 512 * 1024  # 512K
        self._interval = interval  # seconds
        self._start_timer()

    def _start_timer(self):
        timer_handle = functools.partial(self.emit, record=None)
        self._timer = threading.Timer(self._interval, timer_handle)
        self._timer.setDaemon(True)
        self._timer.start()

    def _send_log_file(self):
        jobstate_id = self._dci_context.last_jobstate_id
        r = dci_file.create(self._dci_context, 'logger.txt',
                            self._current_log.getvalue(), 'text/plain',
                            jobstate_id)
        if r.status_code != 201:
            raise DciLogPushFailure(r.json()['message'])
        self._current_log.truncate(0)
        self._current_log.seek(0)

    def emit(self, record):
        # if record is None then emit() is actually run by the timer
        if record is None:
            self.acquire()
            try:
                if len(self._current_log.getvalue()) > 0:
                    self._send_log_file()
            finally:
                self.release()
            self._start_timer()
            return

        msg = u"%s\n" % self.format(record)

        if record.levelno == logging.INFO:
            if self._info_as_jobstate and self._dci_context.last_job_id:
                dci_jobstate.create(
                    self._dci_context,
                    'running',
                    msg.rstrip('\n'), self._dci_context.last_job_id)
                return

        self._current_log.write(msg)
        #  if its an error then send the log
        if record.levelno == logging.ERROR:
            self._send_log_file()
        #  if we reach the current log threshold
        elif len(self._current_log.getvalue()) > self._threshold_log:
            self._send_log_file()


class DciLogPushFailure(Exception):
    """Failed to push log."""
