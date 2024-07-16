%global srcname dciclient
%global summary Python client for DCI control server for the remote CIs

Name:           python-%{srcname}
Version:        4.0.1
Release:        1.VERS%{?dist}
Summary:        %{summary}

License:        ASL 2.0
URL:            https://github.com/redhat-cip/python-%{srcname}
Source0:        %{srcname}-%{version}.postDATE.tar.gz

BuildArch:      noarch

%description
%{summary}

%package -n python3-%{srcname}
Summary: %{summary}
%{?python_provide:%python_provide python3-%{srcname}}
BuildRequires:  python3-prettytable
BuildRequires:  python3-psycopg2
BuildRequires:  python3-requests
BuildRequires:  python3-setuptools
BuildRequires:  python3-rpm-macros
BuildRequires:  python3-dciauth >= 2.1.7
BuildRequires:  python3-devel
Requires:       python3-prettytable
Requires:       python3-requests
Requires:       python3-dciauth >= 2.1.7
Requires:       python3-setuptools

%description -n python3-%{srcname}
%{summary}

%prep
%autosetup -n %{srcname}-%{version}.postDATE

%build
%py3_build

%install
install -d %{buildroot}%{_bindir} %{buildroot}%{_datadir}/python-%{srcname}

%py3_install

%files -n python3-%{srcname}
%doc README.md
%license LICENSE
%{python3_sitelib}/*
%{_bindir}/dcictl
%{_bindir}/dci-vault
%{_bindir}/dci-vault-client
%{_bindir}/dci-rhel-latest-kernel-version
%{_bindir}/dci-create-component
%{_bindir}/dci-create-job
%{_bindir}/dci-find-latest-component
%{_bindir}/dci-diff-jobs


%changelog
* Tue Jul 16 2024 Guillaume Vincent <gvincent@redhat.com> 4.0.1-1
- Drop python 2

* Wed Apr 03 2024 Guillaume Vincent <gvincent@redhat.com> 4.0.0-1
- Replace file-show with file-content
- Update file-show to return file API content
- Remove job-show-file in favor of file-show
- Remove job-delete-file in favor of file-delete

* Thu Jan 25 2024 Frederic Lepied <flepied@redhat.com> 3.5.0-1.VERS.fc38
- add the dci-create-job utility

* Wed Dec 06 2023 Frederic Lepied <flepied@redhat.com> 3.4.4-1
- Fix missing dependency on python-setuptools

* Tue Nov 07 2023 Frederic Lepied <flepied@redhat.com> 3.4.3-1
- Use the new build process compatible with PEP-0440

* Mon Oct 16 2023 Jorge A Gallegos <jgallego@redhat.com> - 3.4.2-1
- Shell printer needs to check vs None

* Fri Sep 29 2023 Jorge A Gallegos <jgallego@redhat.com> - 3.4.1-1
- Fix shell printer for empty response from file download

* Wed Sep 20 2023 Guillaume Vincent <gvincent@redhat.com> 3.4.0-1
- Remove team topic associations on topic module

* Mon Jul 17 2023 François Charlier <fcharlie@redhat.com> 3.3.0-1
- deprecate remoteci keys

* Sun Jun 04 2023 Frederic Lepied <flepied@redhat.com> 3.2.0-1
- add delete_component api

* Tue Apr 04 2023 Yassine Lamgarchal <yassine.lamgarchal@redhat.com> 3.1.0-1
- Removed title and message on component commands
- Added display_name and version on component commands
- Add a new create_v2 on component api

* Tue Jan 10 2023 Guillaume Vincent <gvincent@redhat.com> 3.0.0-1
- Build also python3-dciclient on EL7

* Thu Nov 03 2022 Frederic Lepied <flepied@redhat.com> 2.6.0-1
- add dci-diff-jobs

* Mon Sep 19 2022 Frederic Lepied <flepied@redhat.com> 2.5.0-1
- add dci-find-latest-component

* Sun Sep 04 2022 Frederic Lepied <flepied@redhat.com> 2.4.0-1
- add dci-create-component

* Wed Aug 31 2022 Yassine Lamgarchal <yassine.lamgarchal@redhat.com> - 2.3.0-3
- Add dci-rhel-latest-kernel-version

* Mon Aug 22 2022 Bill Peck <bpeck@redhat.com> - 2.3.0-2
- Rebuild for RHEL-9

* Thu Mar 17 2022 Frederic Lepied <flepied@redhat.com> - 2.3.0-1
- add dci-vault and dci-vault-client

* Thu Jan 20 2022 Guillaume Vincent <gvincent@redhat.com> - 2.2.1-1
- Refactor printers

* Tue Dec 21 2021 Guillaume Vincent <gvincent@redhat.com> - 2.2.0-1
- Add get_or_create base method

* Sat Jun 19 2021 Frederic Lepied <flepied@redhat.com> - 2.1.0-1
- add optional parameters to jobs.create and jobs.schedule

* Tue Apr 13 2021 Guillaume Vincent <gvincent@redhat.com> - 2.0.2-4
- Remove setuptools

* Tue Feb 09 2021 François Charlier <fcharlier@redhat.com> - 2.0.2-3
- Bump python-dciauth version requirement to fix a critical issue with signatures.

* Wed Dec 23 2020 François Charlier <fcharlie@rehdat.com> - 2.0.2-2
- Make explicit dependency to dciauth >= 2.1.5 required since 2.0.2-1

* Fri Dec 04 2020 Guillaume Vincent <gvincent@redhat.com> - 2.0.2-1
- Use HMAC version 2 mechanism on python dciclient

* Mon Nov 02 2020 Haïkel Guémar <hguemar@fedoraproject.org> - 2.0.1-1
- Remove PyYAML

* Mon Sep 14 2020 Guillaume Vincent <gvincent@redhat.com> - 2.0.0-1
- Breaking change: remove capability to manipulate job tags directly in the cli.
- Breaking change: job.delete_tag and component.delete_tag api change.

* Thu Jun 04 2020 Bill Peck <bpeck@redhat.com> - 1.0.4-2
- Rebuild for RHEL-8

* Tue May 26 2020 Guillaume Vincent <gvincent@redhat.com> - 1.0.4-1
- Dont print output if no content or no response

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

* Thu Oct 24 2019 Guillaume Vincent <gvincent@redhat.com> - 0.5.3-1
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
