#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	apcu_bc
Summary:	APCu Backwards Compatibility Module
Name:		%{php_name}-pecl-%{modname}
Version:	1.0.3
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	https://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	2ba61ea2cf887814e702e25ad7f1a5e1
URL:		https://pecl.php.net/package/apcu_bc
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-devel >= 4:7.0.0
BuildRequires:	%{php_name}-pecl-apcu-devel
BuildRequires:	rpmbuild(macros) >= 1.666
%if %{with tests}
BuildRequires:	%{php_name}-pecl-apcu
%endif
%{?requires_php_extension}
Requires:	%{php_name}-pecl-apcu
Provides:	php(apcu) = %{version}
Provides:	php(apcu_bc) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This module provides a backwards APC compatible API using APCu.

%prep
%setup -qc
mv %{modname}-%{version}/* .

cat <<'EOF' > run-tests.sh
#!/bin/sh
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
exec %{__make} test \
	PHP_EXECUTABLE=%{__php} \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="apcu" \
	RUN_TESTS_SETTINGS="-q $*"
EOF
chmod +x run-tests.sh

%build
phpize
%configure
%{__make}

# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{php_extensiondir}/apcu.so \
	-d extension=apc.so \
	-m > modules.log
grep apc modules.log

%if %{with tests}
./run-tests.sh --show-diff
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

# ext filename not important, rename for simplicity
mv $RPM_BUILD_ROOT%{php_extensiondir}/{apc,%{modname}}.so

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README.md
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
