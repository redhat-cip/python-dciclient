#!/bin/bash
set -eux
PROJ_NAME=python-dciclient

# Create the proper filesystem hierarchy to proceed with srpm creatioon
#
rpmdev-setuptree
cp ${PROJ_NAME}.spec ${HOME}/rpmbuild/SPECS/
git archive master --format=tgz --output=${HOME}/rpmbuild/SOURCES/${PROJ_NAME}-0.1.tgz
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
