# TODO:
# - cvsadmin uid,gid
# - check permissions
# - missing files
# - rc-inetd file(?) / init script(?)
Summary:	cvsd, a chroot/suid wrapper for running a cvs pserver
Summary(pl):	cvsd - nak³adka na cvs pserver korzystaj±ca z chroot/suid
Name:		cvsd
Version:	1.0.6
Release:	0.1
License:	GPL
Group:		Development/Version Control
Source0:	http://tiefighter.et.tudelft.nl/~arthur/cvsd/%{name}-%{version}.tar.gz
# Source0-md5:	8432a3d6d2103236b77e4a27dba858cd
#Source1:	%{name}.conf
#Source2:	%{name}-passwd
URL:		http://tiefighter.et.tudelft.nl/~arthur/cvsd/
BuildRequires:	rpmbuild(macros) >= 1.159
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/groupmod
Requires(pre):	cvs
Requires(pre):	/usr/bin/ldd
Requires(pre):	fileutils
Requires(pre):	textutils
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
Requires:	cvs
Provides:	group(cvsadmin)
Provides:	user(cvsowner)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		homedir		/home/cvsowner
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
install -d $RPM_BUILD_ROOT%{rootdir}/{etc,bin,lib,tmp,dev,cvsroot}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

#install %{SOURCE2} $RPM_BUILD_ROOT%{rootdir}/etc/passwd

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`/usr/bin/getgid cvsadmin`" ]; then
	if [ "`/usr/bin/getgid cvsadmin`" != "53" ]; then # 2401
		echo "Error: group cvsadmin doesn't have gid=53. Correct this before installing cvsd." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 53 cvsadmin
fi
if [ -n "`/bin/id -u cvsowner 2>/dev/null`" ]; then
	if [ "`/bin/id -u cvsowner`" != "128" ]; then
		echo "Error: user cvsowner doesn't have uid=128. Correct this before installing cvsd." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 128 -g 53 -c "CVS UID" -d %{homedir} cvsowner
fi
if [ ! -f %{rootdir}/bin/cvs ] ; then
	echo "Setting up %{rootdir}..."
	cd /lib
	install -m755 -o root -g root `ldd /usr/bin/cvs | cut -d " " -f 1` /lib/libnss_files.so.1 \
		%{rootdir}/lib
	install -m755 /usr/bin/cvs %{rootdir}/bin
fi
# TODO: rc-inetd file
#if ! grep -q cvspserver /etc/inetd.conf ; then
#	echo "no existing cvspserver line in /etc/inetd.conf, adding..."
#	echo -e "cvspserver\tstream\ttcp\tnowait\troot\t/usr/sbin/cvsd\tcvsd" >> /etc/inetd.conf
#fi
echo "Now check out /etc/cvsd.conf, restart inetd (killall -HUP inetd), and "
echo "initialise the repository using: "
echo "\"cvs -d :pserver:cvsadmin@localhost:/cvsroot init\" "
echo "Also edit/modify/whatever the /home/cvsowner/cvsd-root/etc/passwd file."
echo "Default user/passwds are cvs/cvs (for ro anon), user/pass. Change these!"

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
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/cvsd/cvsd.conf
#%attr(754,root,root) /etc/rc.d/init.d/cvsd
%{_mandir}/man[58]/*
%dir %{homedir}
%dir %{rootdir}
%dir %{rootdir}/bin
%attr(755,cvsowner,cvsadmin) %dir %{rootdir}/cvsroot
%dir %{rootdir}/dev
%dev(c,1,3) %{rootdir}/dev/null
%dir %{rootdir}/lib
%dir %{rootdir}/tmp
#%config(noreplace) %verify(not size mtime md5) %{rootdir}/etc/passwd
