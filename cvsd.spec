# TODO:
# - cvsadmin uid,gid
# - check permissions
Summary:	cvsd, a chroot/suid wrapper for running a cvs pserver
Summary(pl):	cvsd - nak³adka na cvs pserver korzystaj±ca z chroot/suid
Name:		cvsd
Version:	1.0.9
Release:	0.1
License:	GPL
Group:		Development/Version Control
Source0:	http://ch.tudelft.nl/~arthur/cvsd/%{name}-%{version}.tar.gz
# Source0-md5:	ee67d1a5366f804580c08ca1d48b85fd
Source1:	%{name}.init
#Source1:	%{name}.conf
#Source2:	%{name}-passwd
URL:		http://ch.tudelft.nl/~arthur/cvsd/
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/bin/ldd
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/groupmod
Requires(pre):	cvs
Requires(pre):	fileutils
Requires(pre):	textutils
Requires:	cvs
Requires:	rc-scripts
Provides:	group(cvsadmin)
Provides:	user(cvsowner)
Obsoletes:	cvs-nserver-pserver
Obsoletes:	cvs-pserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		homedir		/var/lib/cvsowner
%define		rootdir		%{homedir}/cvsd-root

%description
cvsd is a chroot/suid wrapper for running a cvs pserver more securely.
cvs is a version control system for managing projects.

%description -l pl
cvsd jest nak³adk± s³u¿±c± do bezpieczniejszego uruchamiania programu
cvs pserver, korzystaj±c± z chroot/suid. cvs jest systemem kontroli
wersji zasobów s³u¿±cym do zarz±dzania projektami.

%prep
%setup -q

%build
%configure

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{rootdir}/{etc,bin,lib,tmp,dev,cvsroot} \
	   $RPM_BUILD_ROOT/etc/rc.d/init.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
#install %{SOURCE2} $RPM_BUILD_ROOT%{rootdir}%{_sysconfdir}/passwd

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 53 cvsadmin
%useradd -u 128 -g 53 -c "CVS UID" -d %{homedir} cvsowner

if [ ! -f %{rootdir}/bin/cvs ] ; then
	echo "Setting up %{rootdir}..."
	cd /lib
	install -m755 -o root -g root `ldd /usr/bin/cvs | cut -d " " -f 1` /lib/libnss_files.so.1 \
		%{rootdir}/lib
	install -m755 /usr/bin/cvs %{rootdir}/bin
fi

%post
/sbin/chkconfig --add cvsd
%service cvsd restart "cvsd"

if [ "$1" = 1 ]; then
%banner -e %{name} <<EOF
Now check out %{_sysconfdir}/cvsd.conf and initialise the repository using:
cvs -d :pserver:cvsadmin@localhost:/cvsroot init

Also edit/modify/whatever the /home/cvsowner/cvsd-root%{_sysconfdir}/passwd file.
Default user/passwds are cvs/cvs (for ro anon), user/pass. Change these!
EOF
fi

%preun
if [ "$1" = "0" ]; then
	%service cvsd stop
	/sbin/chkconfig --del cvsd
fi

%postun
if [ "$1" = "0" ]; then
	%userremove cvsowner
	%groupremove cvsadmin
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog FAQ NEWS README TODO
%attr(755,root,root) %{_sbindir}/cvsd
%attr(755,root,root) %{_sbindir}/cvsd-buildroot
%attr(755,root,root) %{_sbindir}/cvsd-passwd
%dir %{_sysconfdir}/cvsd
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/cvsd/cvsd.conf
%attr(754,root,root) /etc/rc.d/init.d/cvsd
%{_mandir}/man[58]/*
%dir %{homedir}
%dir %{rootdir}
%dir %{rootdir}/bin
%attr(755,cvsowner,cvsadmin) %dir %{rootdir}/cvsroot
%dir %{rootdir}/dev
%dev(c,1,3) %{rootdir}/dev/null
%dir %{rootdir}/lib
%dir %{rootdir}/tmp
#%config(noreplace) %verify(not size mtime md5) %{rootdir}%{_sysconfdir}/passwd
