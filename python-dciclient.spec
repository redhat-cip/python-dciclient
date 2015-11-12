Name:           python-dciclient
Version:        0.1
Release:        1%{?dist}
Summary:        Python client for DCI control server

License:        ASL 2.0
URL:            https://github.com/redhat-cip/python-dciclient
Source0:        python-dciclient-%{version}.tgz

BuildArch:      noarch
BuildRequires:  python2-devel python3-devel

%description
Python client for DCI control server and also the agents
for the remote CIs including tox agent and khaleesi agent.

%package -n python2-dciclient
Summary:        Python client for DCI control server

Requires:       python-prettytable
Requires:       py-bcrypt
Requires:       PyYAML
Requires:       python-requests
Requires:       python-simplejson
Requires:       python-six

%package -n python3-dciclient
Summary:        Python client for DCI control server

Requires:       python3-prettytable
Requires:       python3-py-bcrypt
Requires:       python3-PyYAML
Requires:       python3-requests
Requires:       python3-simplejson
Requires:       python3-six

%description -n python3-dciclient
A Python 3 implementation of the client for DCI control server and also the
agents for the remote CIs including tox agent and khaleesi agent.

%description -n python2-dciclient
A Python 2 implementation of the client for DCI control server and also the
agents for the remote CIs including tox agent and khaleesi agent.

%prep -a
%autosetup

%build
%py2_build
%py3_build

%install
%py2_install
%py3_install

%files -n python2-dciclient
%doc
%{python2_sitelib}/dciclient
%{python2_sitelib}/agents
%{_bindir}/dcictl

%files -n python3-dciclient
%doc
%{python3_sitelib}/dciclient
%{python3_sitelib}/agents
%{_bindir}/dcictl

%changelog
