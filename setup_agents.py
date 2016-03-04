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

import codecs
import os
import setuptools

from dciclient import version


def _get_readme():
    readme_path = '%s/%s' % (os.path.dirname(os.path.abspath(__file__)),
                             'README.md')

    with codecs.open(readme_path, 'r', encoding='utf8') as f:
        return f.read()


setuptools.setup(
    name='dci-agents',
    version=version.__version__,
    packages=['agents'],
    author='Distributed CI team',
    author_email='distributed-ci@redhat.com',
    description='DCI agents for DCI Control Server',
    long_description=_get_readme(),
    install_requires=['dciclient'],
    url='https://github.com/redhat-cip/python-dciclient',
    license='Apache v2.0',
    include_package_data=True,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: System :: Distributed Computing'
    ],
    entry_points={
        'console_scripts': [
            'dci-agent-chainsaw = agents.chainsaw:main',
            'dci-agent-dci = agents.dci:main',
            'dci-agent-tox = agents.tox:main',
        ],
    }
)
