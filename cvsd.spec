Summary: cvsd, a chroot/suid wrapper for running a cvs pserver.
Name: cvsd
Version: 0.6
Release: 1
Copyright: GPL
Group: Development/Version Control
Source0: http://cblack.mokey.com/cvsd/cvsd-0.6.tar.gz
Source1: cvsd.conf
Source2: cvsd-passwd
URL: http://cblack.mokey.com/cvsd/
Packager: Chris Black <cblack@mokey.com>
Requires: cvs
Buildroot: /tmp/%{name}-root

%description
cvsd is a chroot/suid wrapper for running a cvs pserver more securely.
cvs is a version control system for managing projects.

%prep
%setup

%build
make all

%install
#rm -rf $RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}/usr/sbin
mkdir -p ${RPM_BUILD_ROOT}/etc
mkdir -p ${RPM_BUILD_ROOT}/home/cvsowner/cvsd-root/etc

export PREFIX=${RPM_BUILD_ROOT}
#make -e install

%pre
SRCDIR=$PWD
if ! grep -q cvsowner /etc/passwd ; then
	echo "Creating cvsowner, group cvsadmin, and setting up /home/cvsowner..."
	mkdir -p /home/cvsowner
	groupadd -g 2401 cvsadmin
	useradd -u 2401 -g 2401 -c "CVS UID" -m -k /home/cvsowner -G cvsadmin cvsowner
	chown -R cvsowner.cvsadmin /home/cvsowner
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
	chown -R cvsowner.cvsadmin /home/cvsowner
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
%defattr(-,cvsowner,cvsadmin)
%dir /home/cvsowner
%attr(-,root,root) %config(noreplace) /etc/cvsd.conf
%config(noreplace) /home/cvsowner/cvsd-root/etc/passwd
%doc	README
%attr(-,root,root) /usr/sbin/cvsd

%changelog
* Sun May 9 1999 Chris Black
- Updated to 0.6, made %install install cvsd-pass itself.

* Tue May 4 1999 Chris Black
- Made initial rpm spec file and install script.
