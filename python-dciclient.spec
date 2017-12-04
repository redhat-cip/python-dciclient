%if 0%{?fedora}
%global with_python3 1
%endif

Name:           python-dciclient
Version:        0.3.3
Release:        1.VERS%{?dist}

Summary:        Python client for DCI control server
License:        ASL 2.0
URL:            https://github.com/redhat-cip/python-dciclient

Source0:        dciclient-%{version}.tar.gz

BuildArch:      noarch

%description
Python client for DCI control server for the remote CIs.

%package -n python2-dciclient
Summary:        Python client for DCI control server
%{?python_provide:%python_provide python2-dciclient}
BuildRequires:  PyYAML
BuildRequires:  dci-api
BuildRequires:  postgresql
BuildRequires:  postgresql-devel
BuildRequires:  postgresql-server
BuildRequires:  python-click
BuildRequires:  python2-pifpaf
BuildRequires:  python-mock
BuildRequires:  python-prettytable
BuildRequires:  python-psycopg2
BuildRequires:  python-pytest
BuildRequires:  python-requests >= 2.6
BuildRequires:  python-rpm-macros
BuildRequires:  python-six
BuildRequires:  python-tox
BuildRequires:  python2-setuptools
BuildRequires:  python2-rpm-macros
BuildRequires:  python3-rpm-macros
Requires:       PyYAML
%if 0%{?fedora} >= 26
Requires:       python2-bcrypt
%else
Requires:       py-bcrypt
%endif
Requires:       python-click
Requires:       python-configparser
Requires:       python-prettytable
Requires:       python-requests >= 2.6
Requires:       python-simplejson
Requires:       python-six
Requires:       python2-setuptools

%description -n python2-dciclient
A Python 2 implementation of the client for DCI control server.

%if 0%{?with_python3}
%package -n python3-dciclient
Summary:        Python client for DCI control server
%{?python_provide:%python_provide python3-dciclient}

BuildRequires:  postgresql
BuildRequires:  postgresql-server
BuildRequires:  python-tox
BuildRequires:  python3-PyYAML
BuildRequires:  python3-click
BuildRequires:  python3-prettytable
BuildRequires:  python3-psycopg2
BuildRequires:  python3-requests
BuildRequires:  python3-setuptools
BuildRequires:  python3-six
Requires:       python3-PyYAML
Requires:       python3-click
Requires:       python3-prettytable
%if 0%{?fedora} >= 26
Requires:       python3-bcrypt
%else
Requires:       python3-py-bcrypt
%endif
Requires:       python3-requests
Requires:       python3-simplejson
Requires:       python3-six


%description -n python3-dciclient
A Python 3 implementation of the client for DCI control server.
%endif

%prep
%autosetup -n dciclient-%{version}

%build
%py2_build
%if 0%{?with_python3}
%py3_build
%endif

%install
install -d %{buildroot}%{_bindir}
%py2_install
%if 0%{?with_python3}
%py3_install
%endif

%check
PYTHONPATH=%{buildroot}%{python2_sitelib}
export DCI_SETTINGS_MODULE="dciclient.v1.tests.settings"

sh ./dciclient/start_db.sh
sh ./dciclient/start_es.sh

%files -n python2-dciclient
%doc README.md
%license LICENSE
%{python2_sitelib}/*
%{_bindir}/dcictl

%if 0%{?with_python3}
%files -n python3-dciclient
%doc README.md
%license LICENSE
%{python3_sitelib}/*
%{_bindir}/dcictl
%endif


%changelog
* Wed May 31 2017 Yassine Lamgarchal <yassine.lamgarchal@redhat.com> - 0.3.3-1
- Add files_events api
- Add file upload/download api
- Add roles management in dcictl

* Tue May 09 2017 Yanis Guenane <yguenane@redhat.com> - 0.3.0-1
- Lots of things

* Tue Mar 08 2016 Brad Watkins <bwatkins@redhat.com> - 0.1-1
- Add dci-feeder-github sysconfig directory

* Mon Nov 16 2015 Yanis Guenane <yguenane@redhat.com> 0.1-1
- Initial commit
