# TODO:
# - cvsadmin uid,gid, evil postun
# - $RPM_SOURCE_DIR in %pre???!!!
Summary:	cvsd, a chroot/suid wrapper for running a cvs pserver
Summary(pl):	cvsd - nak³adka na cvs pserver korzystaj±ca z chroot/suid
Name:		cvsd
Version:	0.9.19
Release:	0.1
License:	GPL
Group:		Development/Version Control
Source0:	http://tiefighter.et.tudelft.nl/~arthur/cvsd/%{name}-%{version}.tar.gz
# Source0-md5:	2757c59517e59771bd9d249aea760b41
Source1:	%{name}.conf
Source2:	%{name}-passwd
URL:		http://tiefighter.et.tudelft.nl/~arthur/cvsd/
Requires:	cvs
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
%{__make} all

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},{/home/cvsowner/cvsd-root,}%{_sysconfdir}}

export PREFIX=${RPM_BUILD_ROOT}
#make -e install

%clean
rm -rf $RPM_BUILD_ROOT

%pre
SRCDIR=$PWD
if ! grep -q cvsowner /etc/passwd ; then
	echo "Creating cvsowner, group cvsadmin, and setting up /home/cvsowner..."
	mkdir -p /home/cvsowner
	groupadd -g 2401 cvsadmin
	useradd -u 2401 -g 2401 -c "CVS UID" -m -k /home/cvsowner -G cvsadmin cvsowner
	chown -R cvsowner:cvsadmin /home/cvsowner
fi
if [ ! -f /home/cvsowner/cvsd-root ] ; then
	echo "Setting up /home/cvsowner/cvsd-root..."
	cd /home/cvsowner
	mkdir cvsd-root
	cd cvsd-root
	mkdir etc bin lib tmp dev cvsroot
	cd /lib
	install -m755 `ldd /usr/bin/cvs | cut -d " " -f 1` /lib/libnss_files.so.1 /home/cvsowner/cvsd-root/lib/
	install -m755 /usr/bin/cvs /home/cvsowner/cvsd-root/bin/
	install -m644 ${RPM_SOURCE_DIR}/cvsd-pass /home/cvsowner/cvsd-root/etc/passwd
	chown -R cvsowner:cvsadmin /home/cvsowner
	mknod /home/cvsowner/cvsd-root/dev/null c 1 3
fi
if ! grep -q cvspserver /etc/services ; then
	echo "no existing cvspserver line in /etc/services, adding..."
	echo -e "cvspserver\t2401/tcp\t\t# CVS pserver auth" >> /etc/services
fi
if ! grep -q cvspserver /etc/inetd.conf ; then
	echo "no existing cvspserver line in /etc/inetd.conf, adding..."
	echo -e "cvspserver\tstream\ttcp\tnowait\troot\t/usr/sbin/cvsd\tcvsd" >> /etc/inetd.conf
fi
echo "Now check out /etc/cvsd.conf, restart inetd (killall -HUP inetd), and "
echo "initialise the repository using: "
echo "\"cvs -d :pserver:cvsadmin@localhost:/cvsroot init\" "
echo "Also edit/modify/whatever the /home/cvsowner/cvsd-root/etc/passwd file."
echo "Default user/passwds are cvs/cvs (for ro anon), user/pass. Change these!"

%postun
/usr/sbin/userdel cvsowner
/usr/sbin/groupdel cvsadmin

%files
%defattr(644,root,root,755)
%doc README
%dir /home/cvsowner
%attr(-,root,root) %config(noreplace) %{_sysconfdir}/cvsd.conf
%config(noreplace) /home/cvsowner/cvsd-root%{_sysconfdir}/passwd
%attr(-,root,root) %{_sbindir}/cvsd
