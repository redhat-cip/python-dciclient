%{!?__python2: %global __python2 %__python}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

%if 0%{?fedora}
%bcond_without python3
%else
%bcond_with python3
%endif

Name:           python-dciclient
Version:        0.1
Release:        1%{?dist}
Summary:        Python client for DCI control server

License:        ASL 2.0
URL:            https://github.com/redhat-cip/python-dciclient
Source0:        python-dciclient-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python-flake8
BuildRequires:  python-pep8
BuildRequires:  python-hacking
BuildRequires:  python-mock
BuildRequires:  pytest

Requires:       py-bcrypt
Requires:       python-prettytable
Requires:       python-six
Requires:       python-requests
Requires:       PyYAML
Requires:       python-simplejson

%description
Python client for DCI control server and also the agents
for the remote CIs including tox agent and khaleesi agent.

%if %{with python3}
%package -n python3-dciclient
Summary:        Python client for DCI control server
BuildRequires:  python3-flake8
BuildRequires:  python3-pep8
BuildRequires:  python-hacking
BuildRequires:  python3-mock
BuildRequires:  pytest

Requires:       python3-py-bcrypt
Requires:       python3-prettytable
Requires:       python3-six
Requires:       python3-requests
Requires:       python3-PyYAML
Requires:       python3-simplejson

%description -n python3-dciclient
Python client for DCI control server and also the agents
for the remote CIs including tox agent and khaleesi agent.
%endif # with python3

%prep -a
%setup -qc

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python2} setup.py build

%if %{with python3}
CFLAGS="$RPM_OPT_FLAGS" %{__python3} setup.py build
%endif # with python3


%install
rm -rf $RPM_BUILD_ROOT
# Must do the python3 install first because the scripts in /usr/bin are
# overwritten with every setup.py install (and we want the python2 version
# to be the default for now).
%if %{with python3}
%{__python3} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_ROOT/%{python3_sitelib}/*.egg-info
%endif # with python3

%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_ROOT/%{python2_sitelib}/*.egg-info


%files
%doc
# For noarch packages: sitelib
%{python2_sitelib}/dciclient
%{_bindir}/dcictl

%if %{with python3}
%files -n python3-dciclient
%doc
# For noarch packages: sitelib
%{python3_sitelib}/dciclient
%{_bindir}/dcictl
%endif # with python3

%changelog
