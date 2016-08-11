#!/usr/bin/env python
#  -*- coding: utf-8 -*-
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

from ansible.module_utils.basic import *
import fcntl
import six
from dciclient.v1.api import file as dci_file
from dciclient.v1.api import context as dci_context
import os


DOCUMENTATION = '''
---
module: dci_upload
short_description: upload logs from local directory to the dci control server
'''

EXAMPLES = '''
- name: upload local logs
  dci_upload:
    src: <path-logs-directory>
    dci_login: <dci login>
    dci_password: <dci password>
    dci_cs_url: <dci cs url>
'''

def kupload(context, src, dci_status):
    """This function upload logs to dci control server from local logs
    directory.
    """
    jobstate_id = open('%s/%s/jobstate_id' % (src, dci_status)).read()
    print("jobstate-id %s" % jobstate_id)
    status_dir = '%s/%s' % (src, dci_status)
    logs_files = os.listdir(status_dir)
    for dci_file in logs_files:
        if dci_file != 'jobstate_id':
            print("upload file %s" % dci_file)

#files = [os.path.join(search_dir, f) for f in files] # add path to each file
#files.sort(key=lambda x: os.path.getmtime(x))


    # clear directory

    return {'upload': 'hihi'}

def upload(context, src, dci_status):
    """This function upload logs to dci control server from local logs
    directory.
    """

    return {'upload': 'hihi'}


# get the result of each task commands
def v2_runner_on_ok(self, result, **kwargs):
    """Event executed after each command when it succeed. Get the output
    of the command and create a file associated to the current
    jobstate."""

    if 'stdout_lines' in result._result:
        output = '\n'.join(result._result['stdout_lines']) + '\n'
    elif 'msg' in result._result:
        output = '\n'.join(result._result['msg']) + '\n'
    else:
        output = str(result._result)


    if result._task.get_name() != 'setup' and self._mime_type == 'application/junit':
        dci_file.create(
            self._dci_context,
            name=result._task.get_name(),
            content=output.encode('UTF-8'),
            mime=self._mime_type,
            job_id=self._job_id)
    elif result._task.get_name() != 'setup' and output != '\n':
        dci_file.create(
            self._dci_context,
            name=result._task.get_name(),
            content=output.encode('UTF-8'),
            mime=self._mime_type,
            jobstate_id=self._current_jobstate_id)
        self._current_step += 1


def main():

    fields = {
        "src": {"required": True, "type": "str"},
        "dci_status": {"required": True, "type": "str" },
        "dci_login": {"required": True, "type": "str" },
        "dci_password": {"required": True, "type": "str" },
        "dci_cs_url": {"required": True, "type": "str" }
    }

    module = AnsibleModule(argument_spec=fields)

    src = module.params['src']
    dci_status = module.params['dci_status']
    dci_login = module.params['dci_login']
    dci_password = module.params['dci_password']
    dci_cs_url = module.params['dci_cs_url']

    #_dci_context = dci_context.build_dci_context(
    #    dci_cs_url,
    #    dci_login,
    #    dci_password
    #)

    response = upload(None, src, dci_status)
    module.exit_json(changed=True, meta=response)


if __name__ == '__main__':
    main()
