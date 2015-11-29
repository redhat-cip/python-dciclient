# Copyright 2015 Red Hat, Inc.
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

from datetime import datetime
from dciclient.v1.consumers import feeder
from HTMLParser import HTMLParser

import requests


PUDDLE_URL = 'http://download.lab.bos.redhat.com/rel-eng/OpenStack/7.0-RHEL-7/'
COMPONENT_TYPES = ['puddle']
TESTS = ['testnumberone']
DCI_LOGIN='admin'
DCI_PASSWORD='admin'
DCI_CS_URL='http://dci.enovance.com'

class puddleHtmlParser(HTMLParser):
    _puddles = []

    def get_puddles(self):
        return self._puddles

    def get_last_puddle(self):
        return self._puddles[-1:]

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and 'href' == attrs[0][0]:
            try:
                date_object = datetime.strptime(attrs[0][1][:10], '%Y-%m-%d')
                self._puddles.append(attrs[0][1])
            except:
                pass


def _retrieve_event():
    """Detect if a new puddle has been released

    This script is supposed to run on a daily basis, and check if a new puddle
    has been released."""
    r = requests.get(PUDDLE_URL)
    puddleParser = puddleHtmlParser()
    puddleParser.feed(r.content)
    event = None

    # NOTE(spredzy) : when using in real life switch true to
    # if datetime.strptime(puddleParser.get_last_puddle()[:10], '%Y-%m-%d') in ['YESTERDAY', 'TODAY']
    if True:
        event = '%s%s' % (PUDDLE_URL, puddleParser.get_last_puddle()[0])

    return event


def get_puddle_component(componenttype):
    """ """
    #event = _retrieve_event()
    event = "This is just a test"

    if event:
        component = {
            'name': 'Puddle %s' % event,
            'componenttype_id': componenttype,
            'canonical_project_name': 'Puddle Openstack',
            'title': 'Puddle %s' % event,
        }

    return component if event else None


if __name__ == '__main__':
    l_feeder = feeder.Feeder(DCI_CS_URL, DCI_LOGIN, DCI_PASSWORD)
    componenttype_ids = l_feeder.ensure_componenttype(COMPONENT_TYPES)
    test_ids = l_feeder.ensure_test(TESTS)

    puddle_component = get_puddle_component(componenttype_ids[0])
    if puddle_component:
        l_feeder.create_component(puddle_component)
        l_feeder.create_jobdefinition('Puddle today', test_ids[0])
