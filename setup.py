#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2024 Red Hat, Inc
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

# dcibuild can be loaded only when doing the sdist sub-command because
# dci-packaging is extracted at the same level. When doing the other
# sub-commands like build, we extract the version from version.py.
try:
    from dcibuild import sdist, get_version

    sdist.dci_mod = "dciclient"
except:
    sdist = None

    def get_version():
        from dciclient import version

        return version.__version__


def _get_requirements():
    requirements_path = "%s/%s" % (
        os.path.dirname(os.path.abspath(__file__)),
        "requirements.txt",
    )
    with open(requirements_path, "r") as f:
        requirements = f.read()
        # remove the dependencies which comes from url source because
        # it's not supported by install_requires
        return [dep for dep in requirements.split("\n") if not dep.startswith("-e")]


def _get_readme():
    readme_path = "%s/%s" % (os.path.dirname(os.path.abspath(__file__)), "README.md")

    with codecs.open(readme_path, "r", encoding="utf8") as f:
        return f.read()


setuptools.setup(
    name="dciclient",
    version=get_version(),
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    author="Distributed CI team",
    author_email="distributed-ci@redhat.com",
    description="Python client for DCI Control Server",
    long_description=_get_readme(),
    long_description_content_type="text/markdown",
    install_requires=_get_requirements(),
    url="https://github.com/redhat-cip/python-dciclient",
    license="Apache v2.0",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Topic :: System :: Distributed Computing",
    ],
    entry_points={
        "console_scripts": [
            "dcictl = dciclient.shell:main",
            "dci-vault = dciclient.vault:main",
            "dci-vault-client = dciclient.vault_client:main",
            "dci-create-component = dciclient.create_component:main",
            "dci-create-job = dciclient.create_job:main",
            "dci-find-latest-component = dciclient.find_latest_component:main",
            "dci-rhel-latest-kernel-version = dciclient.rhel_kernel:main",
            "dci-diff-jobs = dciclient.diff_jobs:main",
        ]
    },
    cmdclass={
        "sdist": sdist,
    },
)
