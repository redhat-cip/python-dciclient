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

from ConfigParser import SafeConfigParser
from optparse import OptionParser

from dciclient.v1.api import file
from dciclient.v1.api import job
from dciclient.v1.api import jobstate


import fcntl
import mimetypes
import os
import select
import subprocess

import six
import sys


def parse_command_line():
    parser = OptionParser("")
    parser.add_option("-u", "--dci-login", dest="dci_login",
                      help="DCI login")
    parser.add_option("-p", "--dci-password", dest="dci_password",
                      help="DCI password")
    parser.add_option("-a", "--dci-cs-url", dest="dci_cs_url",
                      help="DCI CS url")

    return parser.parse_args()


def get_credentials(options):

    if options.dci_cs_url and options.dci_login and options.dci_password:
        return options.dci_login, options.dci_password, options.dci_cs_url

    if os.environ.get('DCI_LOGIN') and \
       os.environ.get('DCI_PASSWORD') and \
       os.environ.get('DCI_CS_URL'):
        return os.environ.get('DCI_LOGIN'),
        os.environ.get('DCI_PASSWORD'),
        os.environ.get('DCI_CS_URL')

    return load_configfile()


def load_configfile():

    # DCI can load configuration files from 3 locations.
    # This is their order of priority
    #
    # * A path specified in the DCICONFFILE environment variable
    # * In a file .dci.conf located in the user home folder
    # * In a file called  /etc/dci/dci.conf
    #
    possible_conf_files = [os.environ.get('DCICONFFILE'),
                           '~/.dci.conf',
                           '/etc/dci/dci.conf']

    for conf_file in possible_conf_files:
        if os.path.isfile(os.path.expanduser(conf_file)):
            parser = SafeConfigParser().read(conf_file)
            dci_login = parser.get('DEFAULT', 'dci_login')
            dci_password = parser.get('DEFAULT', 'dci_password')
            dci_cs_url = parser.get('DEFAULT', 'dci_cs_url')
            return dci_login, dci_password, dci_cs_url

    return None, None, None


def upload_file(context, path, job_id, mime=None):

    if not mime:
        mime = mimetypes.guess_type(path)[0]

    l_file = file.create(context, name=path, content=open(path, 'r').read(),
                         mime=mime)

    l_file_id = l_file.json()['file']['id']
    job.add_file(context, job_id, l_file_id)


def run_command(context, cmd, cwd, jobstate_id, team_id):
    """This function execute a command and send its log which will be
    attached to a jobstate.
    """
    output = six.StringIO()
    print('* Processing command: %s' % cmd)
    print('* Working directory: %s' % cwd)
    pipe_process = subprocess.Popen(cmd, cwd=cwd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

    fcntl.fcntl(pipe_process.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
    inputs = [pipe_process.stdout]
    outputs = []

    while True:
        readable, writable, exceptional = select.select(inputs, outputs,
                                                        inputs, 60)
        if not readable:
            break
        pstdout = pipe_process.stdout.read().decode('UTF-8', 'ignore')
        if len(pstdout) == 0:
            break
        else:
            print(pstdout)
            output.write(pstdout)

    pipe_process.wait()

    file.create(context, name='_'.join(cmd), content=output.getvalue(),
                mime='text/plain', jobstate_id=jobstate_id)
    output.close()
    return pipe_process.returncode


def run_commands(context, cmds, cwd, jobstate_id, job_id, team_id):
    for cmd in cmds:
        if isinstance(cmd, dict):
            rc = run_command(context, cmd['cmd'], cmd['cwd'], jobstate_id,
                             team_id)
        else:
            rc = run_command(context, cmd, cwd, jobstate_id, team_id)

        if rc != 0:
            error_msg = "Failed on command %s" % cmd
            jobstate.create(context, "failure", error_msg, job_id)
            print(error_msg)
            sys.exit(1)
