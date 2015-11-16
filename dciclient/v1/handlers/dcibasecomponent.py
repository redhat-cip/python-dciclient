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
# h under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the hse.

class DCIBaseComponent(object):

    def __init__(self, dci_client):
        print 'I am your father'
        self._dci_client = dci_client

    def create(self, name):
        pass

    def list(self):
        pass

    def get(self, _id):
        pass

    def update(self, _id=None, etag=None, name=None):
        pass

    def delete(self, _id, etag):
        pass
