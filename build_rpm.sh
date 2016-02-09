#!/bin/bash
set -eux
PROJ_NAME=python-dciclient
DATE=$(date +%Y%m%d%H%M)
SHA=$(git rev-parse HEAD | cut -c1-8)

# Configure rpmmacros to enable signing packages
#
echo '%_signature gpg' >> ~/.rpmmacros
echo '%_gpg_name Distributed-CI' >> ~/.rpmmacros

# Create the proper filesystem hierarchy to proceed with srpm creatioon
#
rm -rf ${HOME}/rpmbuild
rpmdev-setuptree
cp ${PROJ_NAME}.spec ${HOME}/rpmbuild/SPECS/
git archive HEAD --format=tgz --output=${HOME}/rpmbuild/SOURCES/${PROJ_NAME}-0.0.${DATE}git${SHA}.tgz
sed -i "s/VERS/${DATE}git${SHA}/g" ${HOME}/rpmbuild/SPECS/${PROJ_NAME}.spec
rpmbuild -bs ${HOME}/rpmbuild/SPECS/${PROJ_NAME}.spec

# Build the RPMs in a clean chroot environment with mock to detect missing
# BuildRequires lines.
for arch in fedora-23-x86_64 epel-7-x86_64; do

    if [[ "$arch" == "fedora-23-x86_64" ]]; then
        RPATH='fedora/23/x86_64'
    else
        RPATH='el/7/x86_64'
    fi

    # NOTE(spredzy): Include the dci repo in mock env
    #
    mkdir -p ${HOME}/.mock
    cp /etc/mock/${arch}.cfg ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i '$i[dci-devel]' ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i '$iname=Distributed CI - Devel - CentOS 7"' ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i '$ibaseurl=http://dci.enovance.com/repos/development/el/7/x86_64/' ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i '$igpgcheck=0' ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i '$ienabled=1' ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i '$i[dci-extras]' ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i '$iname=Distributed CI - No upstream package - CentOS 7"' ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i '$ibaseurl=http://dci.enovance.com/repos/extras/el/7/x86_64/' ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i '$igpgcheck=0' ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i '$ienabled=1' ${HOME}/.mock/${arch}-with-dci-repo.cfg

    # NOTE(spredzy) Add signing options
    #
    sed -i "\$aconfig_opts['plugin_conf']['sign_enable'] = True" ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i "\$aconfig_opts['plugin_conf']['sign_opts'] = {}" ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i "\$aconfig_opts['plugin_conf']['sign_opts']['cmd'] = 'rpmsign'" ${HOME}/.mock/${arch}-with-dci-repo.cfg
    sed -i "\$aconfig_opts['plugin_conf']['sign_opts']['opts'] = '--addsign %(rpms)s'" ${HOME}/.mock/${arch}-with-dci-repo.cfg

    mkdir -p development
    mock -r ${HOME}/.mock/${arch}-with-dci-repo.cfg rebuild --resultdir=development/${RPATH} ${HOME}/rpmbuild/SRPMS/${PROJ_NAME}*
done
