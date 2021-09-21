#!/usr/bin/env python3
"""system compatibility check before package install"""

import platform
import subprocess
import struct


def get_system_info():
    """gather system architecture and os information."""
    return {
        "os": platform.system(),
        "distro": _get_distro(),
        "arch": platform.machine(),
        "bits": struct.calcsize("P") * 8,
        "kernel": platform.release(),
        "python": platform.python_version(),
    }


def _get_distro():
    """detect linux distribution."""
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("ID="):
                    return line.strip().split("=")[1].strip('"')
    except OSError:
        pass
    return platform.system().lower()


def check_arch_compat(package_arch, system_arch=None):
    """check if package architecture is compatible."""
    if system_arch is None:
        system_arch = platform.machine()
    compat_map = {
        "x86_64": ["x86_64", "amd64", "any", "noarch"],
        "aarch64": ["aarch64", "arm64", "any", "noarch"],
        "armv7l": ["armv7l", "armhf", "any", "noarch"],
    }
    compatible = compat_map.get(system_arch, [system_arch, "any"])
    return package_arch.lower() in [c.lower() for c in compatible]


def check_lib_deps(libraries):
    """check if required shared libraries are available."""
    missing = []
    for lib in libraries:
        try:
            result = subprocess.run(
                ["ldconfig", "-p"],
                capture_output=True, text=True, timeout=5,
            )
            if lib not in result.stdout:
                missing.append(lib)
        except (subprocess.TimeoutExpired, OSError):
            missing.append(lib)
    return missing


def check_kernel_version(min_version):
    """check if kernel meets minimum version requirement."""
    current = platform.release().split("-")[0]
    from update_checker import compare_versions
    return compare_versions(current, min_version) >= 0


def full_compat_check(package_info):
    """run full compatibility check for a package."""
    sys_info = get_system_info()
    results = {
        "system": sys_info,
        "compatible": True,
        "issues": [],
    }
    pkg_arch = package_info.get("arch", "any")
    if not check_arch_compat(pkg_arch):
        results["compatible"] = False
        results["issues"].append(
            f"arch mismatch: {pkg_arch} vs {sys_info['arch']}"
        )
    libs = package_info.get("libraries", [])
    missing = check_lib_deps(libs)
    if missing:
        results["issues"].append(f"missing libs: {missing}")
    return results


if __name__ == "__main__":
    info = get_system_info()
    print("system info:")
    for k, v in info.items():
        print(f"  {k}: {v}")
