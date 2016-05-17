#!/bin/bash -e

source dcirc

#Get or create Topic ID
TOPIC_ID=$(dcictl topic-list | awk '/openstack-ci/ {print $2}')
if [ -z "${TOPIC_ID}" ]; then
  TOPIC_ID=$(dcictl topic-create --name openstack-ci | awk '/id/ {print $4}')
fi

#Get or create Team ID
TEAM_ID=$(dcictl team-list | awk '/openstack-ci/ {print $2}')
if [ -z "${TEAM_ID}" ]; then
  TEAM_ID=$(dcictl team-create --name openstack-ci | awk '/id/ {print $4}')
fi

#Verify teams is in the topic
if [ ! $(dcictl topic-list-team --id ${TOPIC_ID} | grep -q ${TEAM_ID})]; then
  dcictl topic-attach-team --id ${TOPIC_ID} --team_id ${TEAM_ID}
fi
ADMIN_TEAM_ID=$(dcictl team-list | awk '/admin/ {print $2}')
if [ ! $(dcictl topic-list-team --id ${TOPIC_ID} | grep -q ${ADMIN_TEAM_ID}) ]; then
  dcictl topic-attach-team --id ${TOPIC_ID} --team_id ${ADMIN_TEAM_ID}
fi

#Get or create Remote CI ID
REMOTECI_ID=$(dcictl remoteci-list | awk '/openstack-ci/ {print $2}')
if [ -z "${REMOTECI_ID}" ]; then
  REMOTECI_ID=$(dcictl remoteci-create --name openstack-ci --team_id ${TEAM_ID} | awk '/ id / {print $4}')
fi

#Get or create Test ID
TEST_ID=$(dcictl test-list --topic_id ${TOPIC_ID} | awk '/OCI-Tempest/ {print $2}')
if [ -z "${TEST_ID}" ]; then
  TEST_ID=$(dcictl test-create --name OCI-Tempest --topic_id ${TOPIC_ID} | awk '/ id / {print $4}')
fi


echo "---
dci:
    login: ${DCI_LOGIN}
    password: ${DCI_PASSWORD}
    control_server_url: ${DCI_CS_URL}
    team_id: ${TEAM_ID}
    remoteci_id: ${REMOTECI_ID}
    topic_id: ${TOPIC_ID}
    test_id: ${TEST_ID}
jenkins:
    jobs:
      -
    views:
      -
    multijobs:
      -
"
