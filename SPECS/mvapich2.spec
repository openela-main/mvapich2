%{!?python3_sitearch: %global python3_sitearch %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:    mvapich2
%global upstream_ver 2.3.7-1
Version: %{lua: print((string.gsub(rpm.expand("%{upstream_ver}"),"-",".")))}
Release: 1%{?dist}
Summary: OSU MVAPICH2 MPI package
Group:   Development/Libraries
# Richard Fontana wrote in https://bugzilla.redhat.com/show_bug.cgi?id=1333114:
## The mvapich2 source code is predominantly 3-clause BSD with a smattering of
## 2-clause BSD, MIT and proto-MIT licensed source code. Under the license
## abbreviation system inherited from Fedora that set of licenses is adequately
## described as 'BSD and MIT'.
## There are a couple of source files that indicate they are taken from glibc
## with LGPL license notices, but context strongly suggests that the author of
## that particular code placed it under the MIT license (which is consistent
## with the approach to copyright assignment in glibc in which the author
## receives a broad grant-back license permitting sublicensing under terms
## other than LGPL).
License: BSD and MIT
URL:     http://mvapich.cse.ohio-state.edu
Source:  http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-2.3.7-1.tar.gz
Source1: mvapich2.module.in
Source2: mvapich2.macros.in
# We delete bundled stuff in the prep step. The *-unbundle-* patches adjust
# the configure scripts and Makefiles accordingly.
Patch1: 0001-mvapich23-unbundle-contrib-hwloc-and-osu_benchmarks.patch

BuildRequires: gcc-gfortran
BuildRequires: libibumad-devel, libibverbs-devel >= 1.1.3, librdmacm-devel
BuildRequires: python3-devel, perl-Digest-MD5, hwloc-devel, rdma-core-devel
BuildRequires: bison, flex
BuildRequires: autoconf, automake, libtool
BuildRequires: rpm-mpi-hooks, rdma-core-devel, infiniband-diags-devel
%ifarch x86_64
BuildRequires: libpsm2-devel >= 10.3.58
%endif
ExcludeArch: s390 s390x
Provides:  mpi
Requires:  environment-modules

%global common_desc MVAPICH2 is a Message Passing Interface (MPI 3.0) implementation based on MPICH\
and developed by Ohio State University.

%description
%{common_desc}

%package devel
Summary:   Development files for %{name}
Group:     Development/Libraries
Provides:  mpi-devel
Requires:  librdmacm-devel, libibverbs-devel, libibumad-devel
Requires:  %{name}%{?_isa} = %{version}-%{release}
Requires:  gcc-gfortran

%description devel
Contains development headers and libraries for %{name}.

%package doc
Summary:   Documentation files for mvapich2
Group:     Documentation
BuildArch: noarch

%description doc
Additional documentation for mvapich2.

%ifarch x86_64
%package psm2
Summary:   OSU MVAPICH2 MPI package 2.3 for Omni-Path adapters
Group:     Development/Libraries
Provides:  mpi
Requires:  environment-modules

%description psm2
%{common_desc}

This is a version of mvapich2 2.3 that uses the PSM2 transport for Omni-Path
adapters.

%package psm2-devel
Summary:   Development files for %{name}-psm2
Group:     Development/Libraries
Provides:  mpi-devel
Requires:  librdmacm-devel, libibverbs-devel, libibumad-devel
Requires:  %{name}-psm2%{?_isa} = %{version}-%{release}
Requires:  gcc-gfortran

%description psm2-devel
Contains development headers and libraries for %{name}-psm2.

%endif

%prep
%setup -q -n %{name}-%{upstream_ver}
%patch1 -p1
# bundled hwloc, knem kernel module
rm -r contrib/
# limic kernel module
rm -r limic2-0.5.6/
# bundled OSU benchmarks
rm -r osu_benchmarks/

# Remove rpath, part 1
find . -name configure -exec \
    sed -i -r 's/(hardcode_into_libs)=.*$/\1=no/' '{}' ';'

mkdir .default
mv * .default
mv .default default

%ifarch x86_64
cp -pr default psm2
%endif


%build
%set_build_flags
export AR=ar

%ifarch x86_64
%global variant %{name}-psm2
%global libname %{variant}
%global namearch %{variant}-%{_arch}

cd psm2
./configure \
    --prefix=%{_libdir}/%{libname} \
    --exec-prefix=%{_libdir}/%{libname} \
    --bindir=%{_libdir}/%{libname}/bin \
    --sbindir=%{_libdir}/%{libname}/bin \
    --libdir=%{_libdir}/%{libname}/lib \
    --mandir=%{_mandir}/%{namearch} \
    --includedir=%{_includedir}/%{namearch} \
    --sysconfdir=%{_sysconfdir}/%{namearch} \
    --datarootdir=%{_datadir}/%{libname} \
    --docdir=%{_docdir}/%{name} \
    --enable-error-checking=runtime \
    --enable-timing=none \
    --enable-g=mem,dbg,meminit \
    --enable-fast=all \
    --enable-shared \
    --enable-static \
    --enable-fortran=all \
    --enable-cxx \
    --disable-silent-rules \
    --disable-wrapper-rpath \
    --with-hwloc=v2 \
    --with-device=ch3:psm

# Remove rpath, part 2
find . -name libtool -exec \
    sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g;
            s|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' '{}' ';'
make %{?_smp_mflags}
cd ..
%endif

%global variant %{name}
%global libname %{variant}
%global namearch %{variant}-%{_arch}

cd default
./configure \
    --prefix=%{_libdir}/%{libname} \
    --exec-prefix=%{_libdir}/%{libname} \
    --bindir=%{_libdir}/%{libname}/bin \
    --sbindir=%{_libdir}/%{libname}/bin \
    --libdir=%{_libdir}/%{libname}/lib \
    --mandir=%{_mandir}/%{namearch} \
    --includedir=%{_includedir}/%{namearch} \
    --sysconfdir=%{_sysconfdir}/%{namearch} \
    --datarootdir=%{_datadir}/%{libname} \
    --docdir=%{_docdir}/%{name} \
    --enable-error-checking=runtime \
    --enable-timing=none \
    --enable-g=mem,dbg,meminit \
    --enable-fast=all \
    --enable-shared \
    --enable-static \
    --enable-fortran=all \
    --enable-cxx \
    --disable-silent-rules \
    --disable-wrapper-rpath \
    --with-hwloc=v2

# Remove rpath, part 2
find . -name libtool -exec \
    sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g;
            s|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' '{}' ';'
make %{?_smp_mflags}
cd ..


%install
finish_install() {
	local VARIANT="$1"
	local LIBNAME="$VARIANT"
	local NAMEARCH="$VARIANT-%{_arch}"

	local MODULE_TEMPLATE="$2"
	local MACROS_TEMPLATE="$3"
	local FORTRAN_SUBDIR_SUFFIX="$4"

	find %{buildroot}%{_libdir}/$LIBNAME/lib -name \*.la -delete

	mkdir -p %{buildroot}%{_mandir}/$NAMEARCH/man{2,4,5,6,7,8,9,n}
	mkdir -p %{buildroot}/%{_fmoddir}/$LIBNAME$FORTRAN_SUBDIR_SUFFIX
	mkdir -p %{buildroot}/%{python3_sitearch}/$LIBNAME

	# Make the environment-modules file
	mkdir -p %{buildroot}%{_sysconfdir}/modulefiles/mpi
	sed "s#@LIBDIR@#%{_libdir}/$LIBNAME#g;
	     s#@ETCDIR@#%{_sysconfdir}/$NAMEARCH#g;
	     s#@FMODDIR@#%{_fmoddir}/$LIBNAME$FORTRAN_SUBDIR_SUFFIX#g;
	     s#@INCDIR@#%{_includedir}/$NAMEARCH#g;
	     s#@MANDIR@#%{_mandir}/$NAMEARCH#g;
	     s#@PYSITEARCH@#%{python3_sitearch}/$LIBNAME#g;
	     s#@COMPILER@#$NAMEARCH#g;
	     s#@SUFFIX@#_$VARIANT#g" \
		< $MODULE_TEMPLATE \
		> %{buildroot}%{_sysconfdir}/modulefiles/mpi/$NAMEARCH

	# make the rpm config file
	mkdir -p %{buildroot}%{_sysconfdir}/rpm
	# do not expand _arch
	sed "s#@MACRONAME@#${LIBNAME//[-.]/_}#g;
	     s#@MODULENAME@#$NAMEARCH#" \
		< $MACROS_TEMPLATE \
		> %{buildroot}/%{_sysconfdir}/rpm/macros.$NAMEARCH
}

# 'make install' fails to mkdir docdir by itself before installing index.html
mkdir -p %{buildroot}%{_docdir}/%{name}

%ifarch x86_64
cd psm2
%make_install
finish_install %{name}-psm2 %SOURCE1 %SOURCE2 ""
cd ..
%endif

cd default
%make_install
finish_install %{name} %SOURCE1 %SOURCE2 ""
cd ..

%global variant %{name}
%global libname %{variant}
%global namearch %{variant}-%{_arch}

%files
%dir %{_libdir}/%{libname}
%dir %{_libdir}/%{libname}/bin
%dir %{_libdir}/%{libname}/lib
%dir %{_mandir}/%{namearch}
%dir %{_mandir}/%{namearch}/man*
%dir %{_fmoddir}/%{libname}
%dir %{python3_sitearch}/%{libname}

%{_libdir}/%{libname}/bin/hydra_nameserver
%{_libdir}/%{libname}/bin/hydra_persist
%{_libdir}/%{libname}/bin/hydra_pmi_proxy
%{_libdir}/%{libname}/bin/mpichversion
%{_libdir}/%{libname}/bin/mpiexec
%{_libdir}/%{libname}/bin/mpiexec.hydra
%{_libdir}/%{libname}/bin/mpiexec.mpirun_rsh
%{_libdir}/%{libname}/bin/mpiname
%{_libdir}/%{libname}/bin/mpirun
%{_libdir}/%{libname}/bin/mpirun_rsh
%{_libdir}/%{libname}/bin/mpispawn
%{_libdir}/%{libname}/bin/mpivars
%{_libdir}/%{libname}/bin/parkill
%{_libdir}/%{libname}/lib/*.so.*
%{_mandir}/%{namearch}/man1/hydra_*
%{_mandir}/%{namearch}/man1/mpiexec.*
%{_sysconfdir}/modulefiles/mpi/%{namearch}

%files devel
%dir %{_includedir}/%{namearch}
%{_sysconfdir}/rpm/macros.%{namearch}
%{_includedir}/%{namearch}/*
%{_libdir}/%{libname}/bin/mpic++
%{_libdir}/%{libname}/bin/mpicc
%{_libdir}/%{libname}/bin/mpicxx
%{_libdir}/%{libname}/bin/mpif77
%{_libdir}/%{libname}/bin/mpif90
%{_libdir}/%{libname}/bin/mpifort
%{_libdir}/%{libname}/lib/pkgconfig
%{_libdir}/%{libname}/lib/*.a
%{_libdir}/%{libname}/lib/*.so
%{_mandir}/%{namearch}/man1/mpi[cf]*
%{_mandir}/%{namearch}/man3/*

%files doc
%{_docdir}/%{name}

%ifarch x86_64
%global variant %{name}-psm2
%global libname %{variant}
%global namearch %{variant}-%{_arch}

%files psm2
%dir %{_libdir}/%{libname}
%dir %{_libdir}/%{libname}/bin
%dir %{_libdir}/%{libname}/lib
%dir %{_mandir}/%{namearch}
%dir %{_mandir}/%{namearch}/man*
%dir %{_fmoddir}/%{libname}
%dir %{python3_sitearch}/%{libname}

%{_libdir}/%{libname}/bin/hydra_nameserver
%{_libdir}/%{libname}/bin/hydra_persist
%{_libdir}/%{libname}/bin/hydra_pmi_proxy
%{_libdir}/%{libname}/bin/mpichversion
%{_libdir}/%{libname}/bin/mpiexec
%{_libdir}/%{libname}/bin/mpiexec.hydra
%{_libdir}/%{libname}/bin/mpiexec.mpirun_rsh
%{_libdir}/%{libname}/bin/mpiname
%{_libdir}/%{libname}/bin/mpirun
%{_libdir}/%{libname}/bin/mpirun_rsh
%{_libdir}/%{libname}/bin/mpispawn
%{_libdir}/%{libname}/bin/mpivars
%{_libdir}/%{libname}/bin/parkill
%{_libdir}/%{libname}/lib/*.so.*
%{_mandir}/%{namearch}/man1/hydra_*
%{_mandir}/%{namearch}/man1/mpiexec.*
%{_sysconfdir}/modulefiles/mpi/%{namearch}

%files psm2-devel
%dir %{_includedir}/%{namearch}
%{_sysconfdir}/rpm/macros.%{namearch}
%{_includedir}/%{namearch}/*
%{_libdir}/%{libname}/bin/mpic++
%{_libdir}/%{libname}/bin/mpicc
%{_libdir}/%{libname}/bin/mpicxx
%{_libdir}/%{libname}/bin/mpif77
%{_libdir}/%{libname}/bin/mpif90
%{_libdir}/%{libname}/bin/mpifort
%{_libdir}/%{libname}/lib/pkgconfig
%{_libdir}/%{libname}/lib/*.a
%{_libdir}/%{libname}/lib/*.so
%{_mandir}/%{namearch}/man1/mpi[cf]*
%{_mandir}/%{namearch}/man3/*
%endif


%changelog
* Mon Jun 05 2023 Kamal Heib <kheib@redhat.com> - 2.3.7.1-1
- Update to upstream release 2.3.7-1
- Add gating tests
- Resolves: rhbz#2212462

* Thu May 13 2021 Honggang Li <honli@redhat.com> - 2.3.6-1
- Update to upstream stable point release v2.3.6
- Resolves: rhbz#1960073

* Tue Dec 01 2020 Honggang Li <honli@redhat.com> - 2.3.5-1
- Update to upstream stable point release v2.3.5
- Resolves: rhbz#1904914

* Wed Oct 14 2020 Honggang Li <honli@redhat.com> - 2.3.4-1
- Update to upstream stable point release v2.3.4
- Build against hwloc-2.2.0
- Resolves: rhbz#1850084

* Wed Apr 15 2020 Honggang Li <honli@redhat.com> - 2.3.3-1
- Update to upstream stable point release v2.3.3
- Fix floating point exception for non-NUMA machine
- Resolves: rhbz#1815962, rhbz#1814296

* Tue Nov 19 2019 Jarod Wilson <jarod@redhat.com> 2.3.2-2
- Add BR: rdma-core-devel and infiniband-diags-devel for infiniband/mad.h
- Related: rhbz#1708656

* Tue Nov 19 2019 Jarod Wilson <jarod@redhat.com> 2.3.2-1
- Update to upstream stable point release v2.3.2
- Resolves: rhbz#1708656

* Thu Nov 08 2018 Jarod Wilson <jarod@redhat.com> 2.3-5
- Add missing Provides: mpi and Requires: environment-modules to base mvapich2 package
- Resolves: rhbz#1647177

* Tue Sep 25 2018 Jarod Wilson <jarod@redhat.com> 2.3-4
- Clean up build/linker commands to better propagate distro-wide flags
- Explicitly disable ftb, blcr and fuse to prevent rpath flag creep
- Related: rhbz#1624147

* Fri Sep 14 2018 Jarod Wilson <jarod@redhat.com> 2.3-3
- Add missing BR on rpm-mpi-hooks
- Related: rhbz#1628630

* Thu Sep 13 2018 Jarod Wilson <jarod@redhat.com> 2.3-2
- Actually set MPI_PYTHON3_SITEARCH in modules file to fix deps
- Resolves: rhbz#1628630

* Mon Aug 13 2018 Jarod Wilson <jarod@redhat.com> 2.3-1
- Update to upstream v2.3 release
- Initial build for RHEL-8, featuring v2.3 only
- Resolves: #1483744

* Wed Jun 13 2018 Jarod Wilson <jarod@redhat.com> - 2.2-1.4
- Update mvapich23 (TrueScale) bits to 2.3rc2

* Thu Jan 18 2018 Michal Schmidt <mschmidt@redhat.com> - 2.2-1.3
- Rebuild in buildroot with updated RDMA stack.

* Wed Jan 17 2018 Michal Schmidt <mschmidt@redhat.com> - 2.2-1.2
- Add a 2.3b build variant for TrueScale: mvapich23-psm.

* Fri Nov 3 2017 Michal Schmidt <mschmidt@redhat.com> - 2.2-1.1
- Add mvapich2 2.3b as mvapich23 and mvapich23-psm2.

* Mon Mar 27 2017 Michal Schmidt <mschmidt@redhat.com> - 2.2-1
- Update to 2.2 GA.
