Summary:	Call phones from Gmail
Name:		google-talkplugin
Version:	5.38.6.0
Release:	1
License:	Multiple, see http://chrome.google.com/
Group:		Applications/Networking
Source0:	http://dl.google.com/linux/talkplugin/rpm/stable/i386/%{name}-%{version}-1.i386.rpm
# NoSource0-md5:	688df0620a710a75de0922e406522b84
NoSource:	0
Source1:	http://dl.google.com/linux/talkplugin/rpm/stable/x86_64/%{name}-%{version}-1.x86_64.rpm
# NoSource1-md5:	904102bdcf2e709c017c7098bc71313d
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
# hack: replace $org with target path in binaries
org=/opt/google/talkplugin/
%if "%{_lib}" == "lib64"
dst=///////usr/lib64/gtalk/
%else
dst=/////////usr/lib/gtalk/
%endif
# length must be identical!
test $(echo -n "$org" | wc -c) = $(echo -n "$dst" | wc -c)
%{__sed} -i~ -e "s,$org,$dst,g" *.so GoogleTalkPlugin

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir}/gtalk,%{_localedir},%{_browserpluginsdir}}
# pepper
install -p libppgoogletalk.so libppo1d.so $RPM_BUILD_ROOT%{_browserpluginsdir}

# npapi
install -p libnpgoogletalk.so libnpo1d.so $RPM_BUILD_ROOT%{_browserpluginsdir}

# support libs
install -p GoogleTalkPlugin $RPM_BUILD_ROOT%{_libdir}/gtalk
install -p libgoogletalkremoting.so $RPM_BUILD_ROOT%{_libdir}/gtalk
cp -a data $RPM_BUILD_ROOT%{_libdir}/gtalk
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

# FIXME: chrome searches from pepper dir, our browser-plugins can't handle that
# see https://chromium.googlesource.com/chromium/chromium/+/trunk/chrome/common/chrome_paths.cc
%triggerin -- google-chrome
d=%{_libdir}/google-chrome/pepper
test -d "$d" || exit 0
for fn in libppgoogletalk.so libppo1d.so; do
	f=$d/$fn
	test -e $f || ln -sf %{_browserpluginsdir}/$nf $f
done

%triggerun -- google-chrome
if [ "$1" = "0" ] || [ "$2" = "0" ]; then
	rm -f %{_libdir}/google-chrome/pepper/{libppgoogletalk.so,libppo1d.so}
fi

%triggerin -- chromium-browser
d=%{_libdir}/chromium-browser/pepper
test -d "$d" || exit 0
for fn in libppgoogletalk.so libppo1d.so; do
	f=$d/$fn
	test -e $f || ln -sf %{_browserpluginsdir}/$nf $f
done

%triggerun -- chromium-browser
if [ "$1" = "0" ] || [ "$2" = "0" ]; then
	rm -f %{_libdir}/chromium-browser/pepper/{libppgoogletalk.so,libppo1d.so}
fi

%files -f windowpicker.lang
%defattr(644,root,root,755)
%attr(755,root,root) %{_browserpluginsdir}/libnpgoogletalk.so
%attr(755,root,root) %{_browserpluginsdir}/libnpo1d.so
%attr(755,root,root) %{_browserpluginsdir}/libppgoogletalk.so
%attr(755,root,root) %{_browserpluginsdir}/libppo1d.so
%dir %{_libdir}/gtalk
%attr(755,root,root) %{_libdir}/gtalk/GoogleTalkPlugin
%attr(755,root,root) %{_libdir}/gtalk/libgoogletalkremoting.so
%{_libdir}/gtalk/windowpicker.glade
%dir %{_libdir}/gtalk/data
%{_libdir}/gtalk/data/LMspeed_510.emd
%{_libdir}/gtalk/data/SFTprec_120.emd
