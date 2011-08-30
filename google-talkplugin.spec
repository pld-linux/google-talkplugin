Summary:	Call phones from Gmail
Name:		google-talkplugin
Version:	2.2.2.0
Release:	0.5
License:	Multiple, see http://chrome.google.com/
Group:		Applications/Networking
Source0:	http://dl.google.com/linux/talkplugin/rpm/stable/i386/%{name}-%{version}-1.i386.rpm
# Source0-md5:	4b75f6584cf78b7a62f53c4e7e928a7e
Source1:	http://dl.google.com/linux/talkplugin/rpm/stable/x86_64/%{name}-%{version}-1.x86_64.rpm
# Source1-md5:	217114d81cdf0648a9af20ee45935b09
URL:		http://www.google.com/chat/video/
BuildRequires:	rpmbuild(macros) >= 1.453
BuildRequires:	sed >= 4.0
Requires:	browser-plugins >= 2.0
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_enable_debug_packages	0
%define		no_install_post_strip	1

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

V=$(rpm -qp --nodigest --nosignature --qf '%{V}' $SOURCE)
if [ version:$V != version:%{version} ]; then
	exit 1
fi
rpm2cpio $SOURCE | cpio -i -d

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
%{__sed} -i~ -e "s,$org,$dst," *.so GoogleTalkPlugin

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir}/gtalk,%{_datadir}/locale,%{_browserpluginsdir}}
# plugin
install -p libnpgoogletalk*.so libnpgtpo3dautoplugin.so $RPM_BUILD_ROOT%{_browserpluginsdir}
# support libs
install -p lib/*.so $RPM_BUILD_ROOT%{_libdir}/gtalk
# NOTE: 32bit
install -p GoogleTalkPlugin $RPM_BUILD_ROOT%{_libdir}/gtalk
cp -p windowpicker.glade $RPM_BUILD_ROOT%{_libdir}/gtalk

cp -a locale/* $RPM_BUILD_ROOT%{_datadir}/locale

# google dudes don't get the locales right, fixup
mv $RPM_BUILD_ROOT%{_datadir}/locale/{en-GB,en_GB}
mv $RPM_BUILD_ROOT%{_datadir}/locale/{no,nb}
mv $RPM_BUILD_ROOT%{_datadir}/locale/{pt-BR,pt_BR}
mv $RPM_BUILD_ROOT%{_datadir}/locale/{pt-PT,pt}
mv $RPM_BUILD_ROOT%{_datadir}/locale/{zh-CN,zh_CN}
mv $RPM_BUILD_ROOT%{_datadir}/locale/{zh-TW,zh_TW}
# not supported in pld
rm -r $RPM_BUILD_ROOT%{_datadir}/locale/es-419
rm -r $RPM_BUILD_ROOT%{_datadir}/locale/iw

%find_lang windowpicker

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_browser_plugins

%postun
if [ "$1" = 0 ]; then
	%update_browser_plugins
fi

%files -f windowpicker.lang
%defattr(644,root,root,755)
%dir %{_libdir}/gtalk
%attr(755,root,root) %{_libdir}/gtalk/libCg.so
%attr(755,root,root) %{_libdir}/gtalk/libCgGL.so
%attr(755,root,root) %{_libdir}/gtalk/GoogleTalkPlugin
%{_libdir}/gtalk/windowpicker.glade
%attr(755,root,root) %{_browserpluginsdir}/libnpgoogletalk*.so
%attr(755,root,root) %{_browserpluginsdir}/libnpgtpo3dautoplugin.so
