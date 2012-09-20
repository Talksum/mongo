%define _prefix /usr/local
# even though most macros are based on _prefix, /usr/lib/rpm/redhat/macros
# specifically overwrites a couple which will screw us up, so we have to
# explicitly define them here
%define _libdir %{_prefix}/lib
%define _mandir %{_prefix}/share/man

Name: talkdb
Version: 2.1.2
Release: 3%{?dist}
Summary: talkdb client shell and tools
License: AGPL 3.0
URL: http://www.mongodb.org
Group: Applications/Databases

Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: js-devel, readline-devel, boost-devel, pcre-devel
BuildRequires: gcc-c++, scons

%description
MongoDB (from "huMONGOus") is a schema-free document-oriented database.
It features dynamic profileable queries, full indexing, replication
and fail-over support, efficient storage of large binary data objects,
and auto-sharding.

This package provides the mongo shell, import/export tools, and other
client utilities.

%package server
Summary: mongodb server, sharding server, and support scripts
Group: Applications/Databases
Requires: talkdb
Requires(pre): /usr/sbin/useradd
Requires(pre): /usr/sbin/groupadd
Requires(post): chkconfig
Requires(preun): chkconfig

%description server
MongoDB (from "huMONGOus") is a schema-free document-oriented database.

This package provides the mongo server software, mongo sharding server
software, default configuration files, and init.d scripts.

%package devel
Summary: Headers and libraries for mongodb development.
Group: Applications/Databases

%description devel
MongoDB (from "huMONGOus") is a schema-free document-oriented database.

This package provides the mongo static library and header files needed
to develop mongo client software.

%prep
%setup

%build
# scons -%{?_smp_mflags} -prefix=$RPM_BUILD_ROOT%{_prefix} all
scons -j 3 --prefix=$RPM_BUILD_ROOT%{_prefix} all
# XXX really should have shared library here

%install
scons --prefix=$RPM_BUILD_ROOT%{_prefix} install
mkdir -p $RPM_BUILD_ROOT%{_prefix}
# cp -rv BINARIES/usr/bin $RPM_BUILD_ROOT/usr
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
cp debian/*.1 $RPM_BUILD_ROOT%{_mandir}/man1/
# FIXME: remove this rm when mongosniff is back in the package
rm -v $RPM_BUILD_ROOT%{_mandir}/man1/mongosniff.1*
mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d
cp -v rpm/init.d-mongod $RPM_BUILD_ROOT/etc/rc.d/init.d/talkdb
chmod a+x $RPM_BUILD_ROOT/etc/rc.d/init.d/talkdb
mkdir -p $RPM_BUILD_ROOT/etc
cp -v rpm/mongod.conf $RPM_BUILD_ROOT/etc/talkdb.conf
mkdir -p $RPM_BUILD_ROOT/etc/sysconfig
cp -v rpm/mongod.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/talkdb
mkdir -p $RPM_BUILD_ROOT/var/lib/talkdb
mkdir -p $RPM_BUILD_ROOT/var/log/talkdb
mkdir -p $RPM_BUILD_ROOT/var/run/talkdb
touch $RPM_BUILD_ROOT/var/log/talkdb/talkdb.log
cp -v $RPM_BUILD_ROOT%{_bindir}/mongod $RPM_BUILD_ROOT%{_bindir}/talkdb

%clean
scons -c
rm -rf $RPM_BUILD_ROOT

%pre server
if ! /usr/bin/id -g talkdb &>/dev/null; then
    /usr/sbin/groupadd -r talkdb
fi
if ! /usr/bin/id talkdb &>/dev/null; then
    /usr/sbin/useradd -M -r -g talkdb -d /var/lib/mongo -s /bin/false \
	-c talkdb talkdb > /dev/null 2>&1
fi

%post server
if test $1 = 1
then
  /sbin/chkconfig --add talkdb
  /sbin/service talkdb start >/dev/null 2>&1
  %{_bindir}/mongo admin --port=27018 --eval "db.auth('talkdb','talk310');db.addUser('talkdb','talk310')" \
  >/dev/null 2>&1
fi

%preun server
if test $1 = 0
then
  /sbin/chkconfig --del talkdb
fi

%postun server
if test $1 -ge 1
then
  /sbin/service talkdb condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%doc README GNU-AGPL-3.0.txt

%{_bindir}/mongo
%{_bindir}/mongodump
%{_bindir}/mongoexport
%{_bindir}/mongofiles
%{_bindir}/mongoimport
%{_bindir}/mongorestore
# %{_bindir}/mongosniff
%{_bindir}/mongostat
%{_bindir}/bsondump
%{_bindir}/mongotop

%{_mandir}/man1/mongo.1*
%{_mandir}/man1/mongod.1*
%{_mandir}/man1/mongodump.1*
%{_mandir}/man1/mongoexport.1*
%{_mandir}/man1/mongofiles.1*
%{_mandir}/man1/mongoimport.1*
# %{_mandir}/man1/mongosniff.1*
%{_mandir}/man1/mongostat.1*
%{_mandir}/man1/mongorestore.1*
%{_mandir}/man1/bsondump.1*

%files server
%defattr(-,root,root,-)
%config(noreplace) /etc/talkdb.conf
%{_bindir}/mongod
%{_bindir}/talkdb
%{_bindir}/mongos
#%{_mandir}/man1/mongod.1*
%{_mandir}/man1/mongos.1*
/etc/rc.d/init.d/talkdb
%config(noreplace) /etc/sysconfig/talkdb
#/etc/rc.d/init.d/mongos
%attr(0755,talkdb,talkdb) %dir /var/lib/talkdb
%attr(0755,talkdb,talkdb) %dir /var/log/talkdb
%attr(0755,talkdb,talkdb) %dir /var/run/talkdb
%attr(0640,talkdb,talkdb) %config(noreplace) %verify(not md5 size mtime) /var/log/talkdb/talkdb.log

%files devel
%{_includedir}/mongo/*
%{_libdir}/libmongoclient.a
%{_bindir}/mongooplog
%{_bindir}/mongoperf


%changelog
* Fri Sep 19 2012 Shane Taylor <shanet@talksum.com> - 2.1.2-3
- Changed to usr/local

* Fri Sep 19 2012 Shane Taylor <shanet@talksum.com> - 2.1.2-2
- Changed more dirs and filenames to talkdb

* Fri Sep 14 2012 Shane Taylor <shanet@talksum.com> - 2.1.2-1
- Changed to talkdb

* Fri Feb 17 2012 Michael A. Fiedler <michael@10gen.com>
- Added proper pid file usage

* Thu Jan 28 2010 Richard M Kreuter <richard@10gen.com>
- Minor fixes.

* Sat Oct 24 2009 Joe Miklojcik <jmiklojcik@shopwiki.com> - 
- Wrote mongo.spec.
