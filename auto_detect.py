#!/usr/bin/env python3
"""auto-detect system hardware and os for package compatibility"""

import platform
import os
import subprocess


def detect_os():
    """detect operating system and distribution."""
    info = {
        "system": platform.system().lower(),
        "release": platform.release(),
        "machine": platform.machine(),
    }
    if info["system"] == "linux":
        info.update(_detect_linux_distro())
    elif info["system"] == "darwin":
        info["distro"] = "macos"
        info["version"] = platform.mac_ver()[0]
    elif info["system"] == "windows":
        info["distro"] = "windows"
        info["version"] = platform.version()
    return info


def _detect_linux_distro():
    """detect linux distribution from os-release."""
    info = {}
    release_file = "/etc/os-release"
    if os.path.isfile(release_file):
        with open(release_file) as f:
            for line in f:
                line = line.strip()
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                val = val.strip('"')
                if key == "ID":
                    info["distro"] = val
                elif key == "VERSION_ID":
                    info["version"] = val
                elif key == "ID_LIKE":
                    info["family"] = val
    return info


def detect_gpu():
    """detect gpu vendor and model."""
    try:
        result = subprocess.run(
            ["lspci"], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            lower = line.lower()
            if "vga" in lower or "3d" in lower:
                if "nvidia" in lower:
                    return {"vendor": "nvidia", "description": line.split(": ", 1)[-1]}
                elif "amd" in lower or "radeon" in lower:
                    return {"vendor": "amd", "description": line.split(": ", 1)[-1]}
                elif "intel" in lower:
                    return {"vendor": "intel", "description": line.split(": ", 1)[-1]}
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return {"vendor": "unknown"}


def detect_arch():
    """detect cpu architecture for package selection."""
    machine = platform.machine().lower()
    arch_map = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "aarch64": "arm64",
        "arm64": "arm64",
        "armv7l": "armv7",
        "i686": "i686",
        "i386": "i386",
    }
    return arch_map.get(machine, machine)


def get_package_manager():
    """detect the system package manager."""
    managers = [
        ("pacman", "pacman"),
        ("apt", "apt-get"),
        ("dnf", "dnf"),
        ("yum", "yum"),
        ("zypper", "zypper"),
        ("brew", "brew"),
        ("apk", "apk"),
        ("xbps-install", "xbps"),
        ("emerge", "portage"),
        ("nix-env", "nix"),
    ]
    for cmd, name in managers:
        try:
            subprocess.run(
                ["which", cmd], capture_output=True, check=True, timeout=3
            )
            return name
        except (subprocess.CalledProcessError, FileNotFoundError,
                subprocess.TimeoutExpired):
            continue
    return "unknown"


def system_profile():
    """build complete system profile for package compatibility."""
    return {
        "os": detect_os(),
        "arch": detect_arch(),
        "gpu": detect_gpu(),
        "package_manager": get_package_manager(),
    }


if __name__ == "__main__":
    profile = system_profile()
    print("system profile:")
    for key, value in profile.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
