Summary:	Call phones from Gmail
Name:		google-talkplugin
Version:	3.14.17.0
Release:	0.1
License:	Multiple, see http://chrome.google.com/
Group:		Applications/Networking
Source0:	http://dl.google.com/linux/talkplugin/rpm/stable/i386/%{name}-%{version}-1.i386.rpm
# NoSource0-md5:	1416f39d4f53ccba0dc28187108a7650
NoSource:	0
Source1:	http://dl.google.com/linux/talkplugin/rpm/stable/x86_64/%{name}-%{version}-1.x86_64.rpm
# NoSource1-md5:	a05df0c17c3fc9df2c9ae4d9d18de8aa
NoSource:	1
URL:		http://www.google.com/chat/video/
BuildRequires:	rpmbuild(macros) >= 1.453
BuildRequires:	sed >= 4.0
Requires:	browser-plugins >= 2.0
Requires:	lsb-release
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

%build
# must be shorter than: RPATH=/opt/google/talkplugin/lib
chrpath -r %{_libdir}/gtalk libnpgtpo3dautoplugin.so

# hack: replace $org with target path
%if "%{_lib}" == "lib64"
dst=///////usr/lib64/gtalk/
%else
dst=/////////usr/lib/gtalk/
%endif
sed -i -e "s#/opt/google/talkplugin/#$dst#g" *.so GoogleTalkPlugin

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir}/gtalk,%{_localedir},%{_browserpluginsdir}}
# plugin
install -p libgoogletalkremoting.so libnpgoogletalk*.so libnpgtpo3dautoplugin.so libnpo1d.so $RPM_BUILD_ROOT%{_browserpluginsdir}
# support libs
install -p lib/*.so $RPM_BUILD_ROOT%{_libdir}/gtalk
#
install -p GoogleTalkPlugin $RPM_BUILD_ROOT%{_libdir}/gtalk
cp -p windowpicker.glade $RPM_BUILD_ROOT%{_libdir}/gtalk

cp -a locale/* $RPM_BUILD_ROOT%{_localedir}

# google dudes don't get the locales right, fixup
mv $RPM_BUILD_ROOT%{_localedir}/{no,nb}
mv $RPM_BUILD_ROOT%{_localedir}/{pt-PT,pt}

for loc in $RPM_BUILD_ROOT%{_localedir}/*-*; do
	d=$(dirname $loc)
	b=$(basename $loc | tr '-' '_')
	newloc="$d/$b"
	mv $loc $newloc
done

# not supported in pld
rm -r $RPM_BUILD_ROOT%{_localedir}/es_419
rm -r $RPM_BUILD_ROOT%{_localedir}/iw

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
%attr(755,root,root) %{_browserpluginsdir}/libgoogletalkremoting.so
%attr(755,root,root) %{_browserpluginsdir}/libnpgoogletalk*.so
%attr(755,root,root) %{_browserpluginsdir}/libnpgtpo3dautoplugin.so
%attr(755,root,root) %{_browserpluginsdir}/libnpo1d.so
