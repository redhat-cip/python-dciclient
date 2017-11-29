FROM centos:7

LABEL name="DCI CLIENT" version="0.0.2"
MAINTAINER DCI Team <distributed-ci@redhat.com>

ENV container docker

RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;

VOLUME [ "/sys/fs/cgroup" ]

RUN yum -y --setopt=tsflags=nodocs install openssh-server epel-release \
    https://packages.distributed-ci.io/dci-release.el7.noarch.rpm \
    centos-release-openstack-ocata && \
    yum -y --setopt=tsflags=nodocs install python2-dciclient && \
    yum clean all

RUN echo root:root | chpasswd && ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -N ''

RUN systemctl enable sshd

EXPOSE 22

CMD ["/usr/sbin/init"]
