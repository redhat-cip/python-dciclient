#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Red Hat, Inc
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


import json
import os
import subprocess


class Gerrit(object):
    def __init__(self, gerrit_server, vote=False):
        self.user = os.environ.get("GERRIT_USER") or os.getlogin()
        self.server = gerrit_server
        self.vote = vote

    def get_open_reviews(self, gerrit_project, gerrit_filter):
        """Get open reviews from Gerrit."""
        gerrit_filter = (
            'project:%s status:open %s' % (gerrit_project, gerrit_filter))
        reviews = subprocess.check_output(['ssh', '-xp29418', self.server,
                                           '-l', self.user, 'gerrit', 'query',
                                           '--format=json',
                                           gerrit_filter])
        reviews = reviews.decode('utf-8').rstrip().split('\n')[:-1]
        return [json.loads(review) for review in reviews]

    def get_last_patchset(self, review_number):
        """Get the last patchset of a review."""
        lpatchset = subprocess.check_output([
            'ssh', '-xp29418', '-l', self.user,
            self.server, 'gerrit', 'query',
            '--format=JSON',
            '--current-patch-set change:%d' %
            review_number])
        lpatchset = lpatchset.decode('utf-8').rstrip().split('\n')[0]
        return json.loads(lpatchset)

    def review(self, patch_sha, status):
        """Push a score (e.g: -1) on a review."""
        if self.vote:
            subprocess.check_output([
                'ssh', '-xp29418', '-l',
                self.user, self.server,
                'gerrit', 'review', '--verified', status,
                patch_sha])
        else:
            print("[Voting disabled] should put '%s' to review '%s'" % (
                status, patch_sha))

    def list_open_patchsets(self, project, gerrit_filter=''):
        """Generator that returns the last patchsets of all the reviews of
        a given project.
        """

        reviews = self.get_open_reviews(project, gerrit_filter)
        for review in reviews:
            yield self.get_last_patchset(int(review['number']))
