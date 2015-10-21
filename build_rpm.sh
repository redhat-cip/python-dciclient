#!/bin/sh
set -eux

RPMBUILD_DIR="rpmbuild"

RPMBUILD_DIR="$(cd $(dirname "$0") && pwd)/${RPMBUILD_DIR}"

# Create rpmbuild directory
rm -rf ${RPMBUILD_DIR}
mkdir -p ${RPMBUILD_DIR}/BUILD
mkdir ${RPMBUILD_DIR}/RPMS
mkdir ${RPMBUILD_DIR}/SOURCES
mkdir ${RPMBUILD_DIR}/SPECS
mkdir ${RPMBUILD_DIR}/SRPMS

# Create tar ball in ${RPMBUILD_DIR}/SOURCES
git archive master --format=tgz --output=${RPMBUILD_DIR}/SOURCES/python-dciclient-0.1.tgz

# Add spec file into ${RPMBUILD_DIR}/SPECS
cp python-dciclient.spec ${RPMBUILD_DIR}/SPECS/

# Build RPM sources
SRPM=$(rpmbuild -bs /home/builder/python-dciclient/rpmbuild/SPECS/python-dciclient.spec | cut -d' ' -f2)

# Build RPM
mock --rebuild --resultdir=./ ${SRPM}
