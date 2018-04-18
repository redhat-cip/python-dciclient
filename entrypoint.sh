#!/bin/sh

# TODO(guillaume) remove this when we will be able to run test with dci-control-server in build_rpm.sh
sed -i 's#git+http://softwarefactory-project.io/r/dci-control-server#-e ../dci-control-server#g' /opt/dci-client/test-requirements.txt

exec "$@"
