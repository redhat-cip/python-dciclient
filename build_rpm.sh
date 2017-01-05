#!/bin/bash
set -eux
PROJ_NAME=python-dciclient
DATE=$(date +%Y%m%d%H%M)
SHA=$(git log -1 --pretty=tformat:%h)

# Configure rpmmacros to enable signing packages
#
echo '%_signature gpg' >> ~/.rpmmacros
echo '%_gpg_name Distributed-CI' >> ~/.rpmmacros

# Create the proper filesystem hierarchy to proceed with srpm creatioon
#
rm -rf ${HOME}/rpmbuild
rpmdev-setuptree
sed -i "s,__version__ = '\(.*\)',__version__ = '0.0.${DATE}git${SHA}'," dciclient/version.py
python setup.py sdist
cp -v dist/* ${HOME}/rpmbuild/SOURCES/
sed "s/VERS/${DATE}git${SHA}/g" ${PROJ_NAME}.spec > ${HOME}/rpmbuild/SPECS/${PROJ_NAME}.spec

rpmbuild -bs ${HOME}/rpmbuild/SPECS/${PROJ_NAME}.spec

# Build the RPMs in a clean chroot environment with mock to detect missing
# BuildRequires lines.
for arch in fedora-23-x86_64 fedora-24-x86_64 epel-7-x86_64; do
    rpath=$(echo ${arch}|sed s,-,/,g|sed 's,epel,el,')

    # NOTE(spredzy): Include the dci repo in mock env
    mkdir -p ${HOME}/.mock development
    # NOTE(Gonéri): We ignore the last """ from the last line to be able to concat
    # our stuff
    head -n -1 /etc/mock/${arch}.cfg > ${HOME}/.mock/${arch}-with-dci-repo.cfg
    cat <<EOF >> ${HOME}/.mock/${arch}-with-dci-repo.cfg
[dci]
name=Distributed CI - CentOS 7
baseurl=https://packages.distributed-ci.io/repos/current/el/7/x86_64/
gpgcheck=1
gpgkey=https://packages.distributed-ci.io/RPM-GPG-KEY-distributedci
enabled=1

[dci-devel]
name="Distributed CI - Devel - CentOS 7"
baseurl=http://packages.distributed-ci.io/repos/development/el/7/x86_64/
gpgcheck=1
gpgkey=https://packages.distributed-ci.io/RPM-GPG-KEY-distributedci
enabled=1

[centos-openstack-mitaka]
name=CentOS-7 - OpenStack mitaka
baseurl=http://mirror.centos.org/centos/7/cloud/x86_64/openstack-mitaka/
gpgcheck=0
enabled=1
"""
# NOTE(spredzy) Add signing options
#
config_opts['plugin_conf']['sign_enable'] = True
config_opts['plugin_conf']['sign_opts'] = {}
config_opts['plugin_conf']['sign_opts']['cmd'] = 'rpmsign'
config_opts['plugin_conf']['sign_opts']['opts'] = '--addsign %(rpms)s'
config_opts['use_host_resolv'] = False
config_opts['files']['etc/hosts'] = """
127.0.0.1 pypi.python.org
"""
EOF
    mock --no-cleanup-after -r ${HOME}/.mock/${arch}-with-dci-repo.cfg --rebuild --resultdir=development/${rpath} ${HOME}/rpmbuild/SRPMS/${PROJ_NAME}*
done
