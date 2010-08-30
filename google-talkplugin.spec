Summary:	Call phones from Gmail
Name:		google-talkplugin
Version:	1.4.1.0
Release:	0.8
License:	Multiple, see http://chrome.google.com/
Group:		Applications/Networking
Source0:	http://dl.google.com/linux/direct/%{name}_current_i386.deb
# Source0-md5:	876920feee6dfbe393a45efdef05d83c
Source1:	http://dl.google.com/linux/direct/%{name}_current_amd64.deb
# Source1-md5:	d2d48903dbc6ea36cc175898e6d5f7db
URL:		http://www.google.com/chat/voice/
BuildRequires:	rpmbuild(macros) >= 1.453
BuildRequires:	sed >= 4.0
Requires:	browser-plugins >= 2.0
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_enable_debug_packages	0
%define		no_install_post_strip	1

# our openssl does not have this symbol
%define		_noautoreq		libcrypto.so.0.9.8(OPENSSL_0.9.8) libssl.so.0.9.8(OPENSSL_0.9.8)

%description
The Google Talk Plugin is a browser plugin that enables you to use
Google voice and video chat to chat face to face with family and
friends.

%prep
%setup -qcT
%ifarch %{ix86}
SOURCE=%{S:0}
%endif
%ifarch %{x8664}
SOURCE=%{S:1}
%endif

ar x $SOURCE
tar zxf control.tar.gz
tar zxf data.tar.gz

version=$(awk '/Version:/{print $2}' control)
if [ $version != %{version}-1 ]; then
	exit 1
fi

mv .%{_docdir}/google-talkplugin/changelog.Debian.gz .
gzip -d changelog.Debian.gz

mv ./opt/google/talkplugin/* .
#cron/google-talkplugin

%build
# must be shorter than: RPATH=/opt/google/talkplugin/lib
chrpath -r %{_libdir}/gtalk libnpgtpo3dautoplugin.so

# hack: replace $org with target path
org=/opt/google/talkplugin/
src=%{_libdir}/gtalk
len=$(($(echo -n "$src" | wc -c) + 1))
dst=$(echo $org | %{__sed} -re "s,^.{$len},$src"'\\x0,')
%{__sed} -i~ -e "s,$org,$dst," *.so

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir}/gtalk,%{_browserpluginsdir}}
# plugin
install -p libnpgoogletalk64.so libnpgtpo3dautoplugin.so $RPM_BUILD_ROOT%{_browserpluginsdir}
# support libs
install -p lib/*.so $RPM_BUILD_ROOT%{_libdir}/gtalk
# hmmz, 32bit
install -p GoogleTalkPlugin $RPM_BUILD_ROOT%{_libdir}/gtalk

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_browser_plugins

%postun
if [ "$1" = 0 ]; then
	%update_browser_plugins
fi

%files
%defattr(644,root,root,755)
%dir %{_libdir}/gtalk
%attr(755,root,root) %{_libdir}/gtalk/libCg.so
%attr(755,root,root) %{_libdir}/gtalk/libCgGL.so
%attr(755,root,root) %{_libdir}/gtalk/GoogleTalkPlugin
%attr(755,root,root) %{_browserpluginsdir}/libnpgoogletalk64.so
%attr(755,root,root) %{_browserpluginsdir}/libnpgtpo3dautoplugin.so
