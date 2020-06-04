%if 0%{?rhel} && 0%{?rhel} < 8
%global with_python2 1
%global __python /usr/bin/python2
%else
%global with_python3 1
%global __python /usr/bin/python3
%endif

Name:           python-dciclient
Version:        1.0.4
Release:        2.VERS%{?dist}

Summary:        Python client for DCI control server
License:        ASL 2.0
URL:            https://github.com/redhat-cip/python-dciclient

Source0:        dciclient-%{version}.tar.gz

BuildArch:      noarch

%description
Python client for DCI control server for the remote CIs.

%if 0%{?with_python2}
%package -n python2-dciclient
Summary:        Python client for DCI control server
%{?python_provide:%python_provide python2-dciclient}
BuildRequires:  PyYAML
BuildRequires:  python-prettytable
BuildRequires:  python-psycopg2
BuildRequires:  python-requests >= 2.6
BuildRequires:  python-rpm-macros
BuildRequires:  python2-setuptools
BuildRequires:  python2-rpm-macros
BuildRequires:  python-dciauth
Requires:       PyYAML
Requires:       python-prettytable
Requires:       python-requests >= 2.6
Requires:       python2-setuptools
Requires:       python-dciauth

%description -n python2-dciclient
A Python 2 implementation of the client for DCI control server.
%endif

%if 0%{?with_python3}
%package -n python3-dciclient
Summary:        Python client for DCI control server
%{?python_provide:%python_provide python3-dciclient}

BuildRequires:  python3-PyYAML
BuildRequires:  python3-prettytable
BuildRequires:  python3-psycopg2
BuildRequires:  python3-requests
BuildRequires:  python3-setuptools
BuildRequires:  python3-rpm-macros
BuildRequires:  python3-dciauth
Requires:       python3-PyYAML
Requires:       python3-prettytable
Requires:       python3-requests
Requires:       python3-dciauth

%description -n python3-dciclient
A Python 3 implementation of the client for DCI control server.
%endif

%prep
%autosetup -n dciclient-%{version}

%build
%if 0%{?with_python2}
%py2_build
%endif
%if 0%{?with_python3}
%py3_build
%endif

%install
install -d %{buildroot}%{_bindir}
%if 0%{?with_python2}
%py2_install
%endif
%if 0%{?with_python3}
%py3_install
%endif

%if 0%{?with_python2}
%files -n python2-dciclient
%doc README.md
%license LICENSE
%{python2_sitelib}/*
%{_bindir}/dcictl
%endif

%if 0%{?with_python3}
%files -n python3-dciclient
%doc README.md
%license LICENSE
%{python3_sitelib}/*
%{_bindir}/dcictl
%endif


%changelog
* Thu Jun 04 2020 Bill Peck <bpeck@redhat.com> - 1.0.4-2
- Rebuild for RHEL-8

* Tue May 26 2020 Guillaume Vincent <gvincent@redhat.com> - 1.0.4-1
- Dont print output if no content or no respopnse

* Tue May 12 2020 Guillaume Vincent <gvincent@redhat.com> - 1.0.3-1
- Fix file download issue

* Tue May 12 2020 Guillaume Vincent <gvincent@redhat.com> - 1.0.2-1
- Fix job-download-file issue

* Wed May 06 2020 Haïkel Guémar <hguemar@fedoraproject.org> - 1.0.1-1
- Bump to 1.0.1 to match pypi release

* Fri Apr 17 2020 Haïkel Guémar <hguemar@fedoraproject.org> - 1.0.0-1
- Remove click
- Remove six

* Thu Jan 30 2020 Haïkel Guémar <hguemar@fedoraproject.org> - 0.7.0-2
- Add six to the requirements
- Fix BR pulling python3 package when building python2 package

* Wed Jan 15 2020 Guillaume Vincent <gvincent@redhat.com> - 0.7.0-1
- Add methods to tag components

* Tue Oct 24 2019 Guillaume Vincent <gvincent@redhat.com> - 0.5.3-1
- Release new version

* Mon Oct 21 2019 Yassine Lamgarchal <yassine.lamgarchal@redhat.com> - 0.5.2-1
- Add tag api
- Add export_control to topic

* Wed Nov 15 2017 Guillaume Vincent <gvincent@redhat.com> - 0.5.1-1
- Remove DCI_SETTINGS_MODULE because tests.settings don't exists anymore

* Wed Nov 15 2017 Guillaume Vincent <gvincent@redhat.com> - 0.5-1
- Add HMAC authentication with python-dciauth

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
