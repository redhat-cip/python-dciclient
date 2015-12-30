#!/bin/bash
set -eux
PROJ_NAME=python-dciclient
DATE=$(date +%Y%m%d%H%M)
SHA=$(git rev-parse HEAD | cut -c1-8)

# Create the proper filesystem hierarchy to proceed with srpm creatioon
#
rm -rf ${HOME}/rpmbuild
rpmdev-setuptree
cp ${PROJ_NAME}.spec ${HOME}/rpmbuild/SPECS/
git archive master --format=tgz --output=${HOME}/rpmbuild/SOURCES/${PROJ_NAME}-0.1.${DATE}git${SHA}.tgz
sed -i "s/VERS/${DATE}git${SHA}/g" ${HOME}/rpmbuild/SPECS/${PROJ_NAME}.spec
rpmbuild -bs ${HOME}/rpmbuild/SPECS/${PROJ_NAME}.spec

# Build the RPMs in a clean chroot environment with mock to detect missing
# BuildRequires lines.
for arch in fedora-22-x86_64 fedora-23-x86_64 epel-7-x86_64; do

    if [[ "$arch" == "fedora-23-x86_64" ]]; then
        RPATH='fedora/23/x86_64'
    elif [[ "$arch" == "fedora-22-x86_64" ]]; then
        RPATH='fedora/22/x86_64'
    else
        RPATH='el/7/x86_64'
    fi

    mkdir -p development
    mock -r $arch rebuild --resultdir=development/${RPATH} ${HOME}/rpmbuild/SRPMS/${PROJ_NAME}*
done
