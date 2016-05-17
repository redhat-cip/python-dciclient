#!/bin/bash -e

source dcirc

#Get or create Topic ID
TOPIC_ID=$(dcictl topic-list | grep openstack-ci | awk '{print $2}')
if [ "$TOPIC_ID" == "" ]; then
  TOPIC_ID=$(dcictl topic-create --name openstack-ci | grep id | awk '{print $4}')
fi

#Get or create Team ID
TEAM_ID=$(dcictl team-list | grep openstack-ci | awk '{print $2}')
if [ "$TEAM_ID" == "" ]; then
  TEAM_ID=$(dcictl team-create --name openstack-ci | grep id | awk '{print $4}')
fi

#Verify teams is in the topic
if [ $(dcictl topic-list-team --id ${TOPIC_ID} | grep ${TEAM_ID} |wc -l ) -ne 1 ]; then
  dcictl topic-attach-team --id $TOPIC_ID --team_id $TEAM_ID
fi
ADMIN_TEAM_ID=$(dcictl team-list | grep admin | awk '{print $2}')
if [ $(dcictl topic-list-team --id ${TOPIC_ID} | grep ${ADMIN_TEAM_ID} |wc -l ) -ne 1 ]; then
  dcictl topic-attach-team --id ${TOPIC_ID} --team_id ${ADMIN_TEAM_ID}
fi

#Get or create Remote CI ID
REMOTECI_ID=$(dcictl remoteci-list | grep openstack-ci | awk '{print $2}')
if [ "$REMOTECI_ID" == "" ]; then
  REMOTECI_ID=$(dcictl remoteci-create --name openstack-ci --team_id $TEAM_ID | grep " id " | awk '{print $4}')
fi

#Get or create Test ID
TEST_ID=$(dcictl test-list --topic_id ${TOPIC_ID} | grep OCI-Tempest | awk '{print $2}')
if [ "$TEST_ID" == "" ]; then
  TEST_ID=$(dcictl test-create --name OCI-Tempest --topic_id ${TOPIC_ID} | grep " id " | awk '{print $4}')
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
