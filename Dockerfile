FROM centos:7

LABEL name="DCI CLIENT"
MAINTAINER DCI Team <distributed-ci@redhat.com>

RUN yum -y install epel-release && \
    yum -y install python python-devel python-tox python2-pip && \
    yum clean all

RUN mkdir /opt/python-dciclient
WORKDIR /opt/python-dciclient
COPY requirements.txt /opt/python-dciclient/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /opt/python-dciclient/

ENV PYTHONPATH /opt/python-dciclient

CMD ["tail", "-f", "/dev/null"]
