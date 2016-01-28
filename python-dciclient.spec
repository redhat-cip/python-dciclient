%if 0%{?fedora}
%global with_python3 1
%endif

Name:           python-dciclient
Version:        0.0.VERS
Release:        1%{?dist}

Summary:        Python client for DCI control server
License:        ASL 2.0
URL:            https://github.com/redhat-cip/python-dciclient

Source0:        python-dciclient-%{version}.tgz

BuildArch:      noarch

%description
Python client for DCI control server and also the agents
for the remote CIs including tox agent and khaleesi agent.

%package -n python2-dciclient
Summary:        Python client for DCI control server
%{?python_provide:%python_provide python2-dciclient}

BuildRequires:  python2-devel
BuildRequires:  python-setuptools

Requires:       python-prettytable
Requires:       py-bcrypt
Requires:       python-click
Requires:       PyYAML
Requires:       python-requests
Requires:       python-simplejson
Requires:       python-six

%description -n python2-dciclient
A Python 2 implementation of the client for DCI control server and also the
agents for the remote CIs including tox agent and khaleesi agent.

%if 0%{?with_python3}
%package -n python3-dciclient
Summary:        Python client for DCI control server
%{?python_provide:%python_provide python3-dciclient}

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires:       python3-prettytable
Requires:       python3-py-bcrypt
Requires:       python3-click
Requires:       python3-PyYAML
Requires:       python3-requests
Requires:       python3-simplejson
Requires:       python3-six

%description -n python3-dciclient
A Python 3 implementation of the client for DCI control server and also the
agents for the remote CIs including tox agent and khaleesi agent.
%endif

%prep -a
%setup -qc

%build
%py2_build
%if 0%{?with_python3}
%py3_build
%endif

%install
%py2_install
find %{buildroot}/%{python2_sitelib}/*.egg-info -name 'requires.txt' | xargs sed -i '1s/bcrypt.*//'
find %{buildroot}/%{python2_sitelib}/*.egg-info -name 'requires.txt' | xargs sed -i '4s/2.7.0/2.6.0/'
find %{buildroot}/%{python2_sitelib}/*.egg-info -name 'requires.txt' | xargs sed -i '7s/click.*/click/'
find %{buildroot}/%{python2_sitelib}/*.egg-info -name 'requires.txt' | xargs sed -i '8s/setuptools.*/setuptools/'
%if 0%{?with_python3}
%py3_install
find %{buildroot}/%{python3_sitelib}/*.egg-info -name 'requires.txt' | xargs sed -i '1s/bcrypt.*//'
find %{buildroot}/%{python3_sitelib}/*.egg-info -name 'requires.txt' | xargs sed -i '4s/2.7.0/2.6.0/'
find %{buildroot}/%{python3_sitelib}/*.egg-info -name 'requires.txt' | xargs sed -i '7s/click.*/click/'
find %{buildroot}/%{python3_sitelib}/*.egg-info -name 'requires.txt' | xargs sed -i '8s/setuptools.*/setuptools/'
%endif

%files -n python2-dciclient
%doc
%{python2_sitelib}/agents
%{python2_sitelib}/feeders
%{python2_sitelib}/dciclient
%{python2_sitelib}/*.egg-info
%{_bindir}/dcictl
%{_bindir}/dci-feeder-dummy
%{_bindir}/dci-agent-helloworld

%if 0%{?with_python3}
%files -n python3-dciclient
%doc
%{python3_sitelib}/agents
%{python3_sitelib}/feeders
%{python3_sitelib}/dciclient
%{python3_sitelib}/*.egg-info
%{_bindir}/dcictl
%{_bindir}/dci-feeder-dummy
%{_bindir}/dci-agent-helloworld
%endif

%changelog
* Mon Nov 16 2015 Yanis Guenane <yguenane@redhat.com> 0.1-1
- Initial commit
