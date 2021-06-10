# Defining the package namespace
%global ns_name ea
%global ns_dir /opt/cpanel

%global _scl_prefix      %{ns_dir}
%global scl_name_prefix  %{ns_name}-
%global scl_name_base    ruby
%global scl_name_version 27
%global scl              %{scl_name_prefix}%{scl_name_base}%{scl_name_version}
%scl_package %scl

# Do not produce empty debuginfo package.
%global debug_package %{nil}

# Support SCL over NFS.
%global nfsmountable 1

# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4586 for more details
%define release_prefix 8

%{!?install_scl: %global install_scl 1}

Summary: Package that installs %scl
Name:    %scl_name
Version: 2.7.2
Release: %{release_prefix}%{?dist}.cpanel
Vendor:  cPanel, Inc.
License: GPLv2+

Source0: README.md
Source1: LEGAL
%if 0%{?install_scl}
Requires: %{scl_prefix}ruby
%endif
BuildRequires: help2man
BuildRequires: scl-utils-build

%description
This is the main package for %scl Software Collection.

%package runtime
Summary: Package that handles %scl Software Collection.
Requires: scl-utils
Requires: %{scl_prefix}ruby-devel

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%post
scl enable %{scl} 'gem install irb --no-document' || :
scl enable %{scl} 'gem install racc --no-document' || :
scl enable %{scl} 'gem install bundler --no-document' || :

%preun

if [ $1 = 0 ]; then
    scl enable %{scl} 'gem uninstall irb'  || :
    scl enable %{scl} 'gem uninstall racc'  || :
    scl enable %{scl} 'gem uninstall bundler'  || :
fi

%package build
Summary: Package shipping basic build configuration
Requires: scl-utils-build
Requires: %{scl_prefix}scldevel

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%package scldevel
Summary: Package shipping development files for %scl
Provides: scldevel(%{scl_name_base})

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.

%prep
%setup -T -c

%if 0%{rhel} < 8
cat <<EOF | tee enable
export PATH=%{_bindir}:%{_sbindir}\${PATH:+:\${PATH}}
export LD_LIBRARY_PATH=%{_libdir}:/opt/cpanel/ea-openssl11/%{_lib}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
export MANPATH=%{_mandir}:\$MANPATH
export PKG_CONFIG_PATH=%{_libdir}/pkgconfig\${PKG_CONFIG_PATH:+:\${PKG_CONFIG_PATH}}
# For SystemTap.
export XDG_DATA_DIRS=%{_datadir}:\${XDG_DATA_DIRS:-/usr/local/share:/usr/share}
EOF
%else
cat <<EOF | tee enable
export PATH=%{_bindir}:%{_sbindir}\${PATH:+:\${PATH}}
export MANPATH=%{_mandir}:\$MANPATH
export PKG_CONFIG_PATH=%{_libdir}/pkgconfig\${PKG_CONFIG_PATH:+:\${PKG_CONFIG_PATH}}
# For SystemTap.
export XDG_DATA_DIRS=%{_datadir}:\${XDG_DATA_DIRS:-/usr/local/share:/usr/share}
EOF
%endif

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat > README << EOF
%{expand:%(cat %{SOURCE0})}
EOF

cp %{SOURCE1} .

%build
# Generate a helper script that will be used by help2man.
cat > h2m_help << 'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_help

# Generate the man page from include.h2m and ./h2m_help --help output.
help2man -N --section 7 ./h2m_help -o %{scl_name}.7

%install
%scl_install

install -D -m 644 enable %{buildroot}%{_scl_scripts}/enable

# Some gems install scripts/bnaries into /opt/cpanel/ea-ruby24/root/usr/local/bin
sed -i 's|PATH=|PATH=%{_bindir}/../local/bin:|' %{buildroot}%{_scl_scripts}/enable

cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

# Install generated man page.
mkdir -p %{buildroot}%{_mandir}/man7/
install -p -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/

# Create directory for pkgconfig files, originally provided by pkgconfig
# package, but not for SCL.
mkdir -p %{buildroot}%{_libdir}/pkgconfig

%files

%files runtime
%doc README LEGAL
%scl_files
# Own the manual directories (rhbz#1073458, rhbz#1072319).
%dir %{_mandir}/man7
%dir %{_libdir}/pkgconfig
%{_mandir}/man7/%{scl_name}.*

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Tue Jun 08 2021 Travis Holloway <t.holloway@cpanel.net> - 2.7.2-8
- EA-9801: Reduce time needed to install this package

* Tue May 11 2021 Travis Holloway <t.holloway@cpanel.net> - 2.7.2-7
- EA-9759: Ensure ruby-devel is properly required

* Tue Mar 09 2021 Travis Holloway <t.holloway@cpanel.net> - 2.7.2-6
- EA-9609: Install racc and irb and require ruby-devel for update to 2.7.2
  Adjusted release to -6 in order to match ea-ruby27 package

* Thu Feb 25 2021 Cory McIntire <cory@cpanel.net> - 2.7.2-1
- EA-9609: Update ea-ruby27 from v2.7.1 to v2.7.2

* Wed Nov 25 2020 Julian Brown <julian.brown@cpanel.net> - 2.7.1-2
- ZC-8005: Replace ea-openssl11 with system openssl on C8

* Thu Aug 13 2020 Julian Brown <julian.brown@cpanel.net> - 2.7.1-1
* Initial commits for Ruby 2.7

