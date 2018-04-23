FROM centos:7

LABEL name="DCI CLIENT" version="0.0.2"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8

RUN yum -y install epel-release && \
    yum -y install gcc && \
    yum -y install python python2-devel python2-pip python2-setuptools && \
    yum -y install python34 python34-devel python34-pip python34-setuptools && \
    yum clean all

RUN pip install -U pip
# python-tox is broken, install tox with pip instead
RUN pip install -U tox

WORKDIR /opt/python-dciclient
ADD requirements.txt /opt/python-dciclient/
RUN pip install -r requirements.txt
ADD . /opt/python-dciclient/

ENV PYTHONPATH /opt/python-dciclient
ENV DISABLE_DB_START 1

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["tail", "-f", "/dev/null"]
