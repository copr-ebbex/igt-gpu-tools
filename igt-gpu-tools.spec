%global gitcommit 03779dd3de8a57544f124d9952a6d2b3e34e34ca
%global gitdate 20190628
%global gitrev .%{gitdate}git%(c=%{gitcommit}; echo ${c:0:7})

Name:           igt-gpu-tools
Version:        1.23
Release:        1%{?gitrev}%{?dist}
Summary:        Test suite and tools for DRM drivers

License:        MIT
URL:            https://gitlab.freedesktop.org/drm/igt-gpu-tools

%if 0%{?gitdate}
Source0:        igt-gpu-tools-%{gitdate}.tar.bz2
%else
Source0:        https://gitlab.freedesktop.org/drm/igt-gpu-tools/-/archive/igt-gpu-tools-%{version}/igt-gpu-tools-igt-gpu-tools-%{version}.tar.bz2
%endif
Source1:        make-git-snapshot.sh

%global provobs_version 2.99.917-42.20180618
Provides:       xorg-x11-drv-intel-devel = %{provobs_version}
Provides:       intel-gpu-tools = %{provobs_version}
Obsoletes:      xorg-x11-drv-intel-devel < %{provobs_version}
Obsoletes:      intel-gpu-tools < %{provobs_version}

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  flex bison
BuildRequires:  pkgconfig(libdrm) >= 2.4.82
BuildRequires:  pkgconfig(pciaccess) >= 0.10
BuildRequires:  pkgconfig(libkmod)
BuildRequires:  pkgconfig(libprocps)
%ifnarch s390x
BuildRequires:  pkgconfig(libunwind)
%endif
BuildRequires:  pkgconfig(libdw)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(valgrind)
BuildRequires:  pkgconfig(cairo) > 1.12.0
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gsl)
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(xmlrpc)
BuildRequires:  pkgconfig(xmlrpc_util)
BuildRequires:  pkgconfig(xmlrpc_client)
BuildRequires:  pkgconfig(json-c)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  kernel-headers
BuildRequires:  pkgconfig(gtk-doc)
BuildRequires:  python3-docutils

%description
igt-gpu-tools (formerly known as intel-gpu-tools) is the standard for writing
test cases for DRM drivers. It also includes a handful of useful tools for
various drivers, such as Intel's GPU tools for i915.

%package docs
Summary:        Documentation for igt-gpu-tools

%description docs
gtk-doc generated documentation package for igt-gpu-tools.

%prep
%autosetup -c -p1

%build
%ifnarch s390x
%global with_libunwind enabled
%else
%global with_libunwind disabled
%endif

# Some explanations here
# - We don't build overlay yet due to Fedora not shipping /usr/bin/leg, but we
#   probably don't care about that anyway
# - We specify -Db_ndebug=false because upstream has explicitly stated that
#   anything else is officially unsupported
# - Attempting to resolve all of the symbols within IGT at executable start
#   causes some of igt's symbols to be resolved in the wrong order, resulting in
#   certain runtime function resolvers (e.g. __attribute__((ifunc))) attempting
#   to call functions which have not been resolved yet - causing everything to
#   segfault. Because of this, we specify "-Dc_link_args=-z lazy" to force lazy
#   symbol resolution.
%meson \
        -Db_ndebug=false \
        -Dc_link_args="-z lazy" \
        -Dbuild_overlay=disabled \
        -Dwith_libdrm=auto \
        -Dwith_libunwind=%{with_libunwind}
%meson_build

%install
%meson_install

%ifarch %{ix86} x86_64
rm %{buildroot}/%{_libdir}/pkgconfig/intel-gen4asm.pc
%endif

# Remove the unversioned libigt symlinks
rm %{buildroot}/%{_libdir}/libigt.so
rm %{buildroot}/%{_libdir}/intel_aubdump.so

%check
# We can't use the default meson_test macro because it makes the annoying
# mistake of running tests through ninja directly instead of through meson,
# which makes it impossible to specify a timeout multiplier. For context, the
# timeout multiplier here is required due to certain tests timing out on koji
# builders that are under heavy load.
%__meson test -C %{_vpath_builddir} --num-processes $(nproc) --print-errorlogs --timeout-multiplier 8 --no-rebuild

%files
%license COPYING
%ifarch %{ix86} x86_64
%{_bindir}/intel-gen4asm
%{_bindir}/intel-gen4disasm
%{_bindir}/intel_dump_decode
%{_bindir}/intel_error_decode
%{_bindir}/intel_framebuffer_dump
%{_bindir}/intel_perf_counters
%endif
%{_libdir}/intel_aubdump.so.0
%{_libdir}/libigt.so.0
%{_libexecdir}/igt-gpu-tools/*
%{_datadir}/igt-gpu-tools/*
%{_bindir}/dpcd_reg
%{_bindir}/igt_*
%{_bindir}/intel_aubdump
%{_bindir}/intel_audio_dump
%{_bindir}/intel_backlight
%{_bindir}/intel_bios_dumper
%{_bindir}/intel_display_crc
%{_bindir}/intel_display_poller
%{_bindir}/intel_dp_compliance
%{_bindir}/intel_firmware_decode
%{_bindir}/intel_forcewaked
%{_bindir}/intel_gem_info
%{_bindir}/intel_gpu_abrt
%{_bindir}/intel_gpu_frequency
%{_bindir}/intel_gpu_time
%{_bindir}/intel_gpu_top
%{_bindir}/intel_gtt
%{_bindir}/intel_guc_logger
%{_bindir}/intel_gvtg_test
%{_bindir}/intel_infoframes
%{_bindir}/intel_l3_parity
%{_bindir}/intel_lid
%{_bindir}/intel_opregion_decode
%{_bindir}/intel_panel_fitter
%{_bindir}/intel_reg
%{_bindir}/intel_reg_checker
%{_bindir}/intel_residency
%{_bindir}/intel_stepping
%{_bindir}/intel_vbt_decode
%{_bindir}/intel_watermark
%{_mandir}/man1/intel_*.1*

%files docs
%license COPYING
%{_datadir}/gtk-doc/html/igt-gpu-tools/*

%changelog
* Fri Jun 28 2019 Lyude Paul <lyude@redhat.com> - 1.23-1.20190628git03779dd
- New git snapshot

* Wed Jun 26 2019 Lyude Paul <lyude@redhat.com> - 1.23-1.20190626git15ad664
- New git snapshot

* Fri Jun 21 2019 Lyude Paul <lyude@redhat.com> - 1.23-1.20190621git22850c1
- New git snapshot

* Wed Jun 19 2019 Lyude Paul <lyude@redhat.com> - 1.23-1.20190619gitc88ced7
- New git snapshot

* Fri May 31 2019 Lyude Paul <lyude@redhat.com> - 1.23-1.20190531git4108c74
- New git snapshot

* Wed May 22 2019 Lyude Paul <lyude@redhat.com> - 1.23-1.20190522gitadf9f43
- New git snapshot

* Thu May 16 2019 Lyude Paul <lyude@redhat.com> - 1.23-1.20190516git555019f
- Initial package

# vim: expandtab
