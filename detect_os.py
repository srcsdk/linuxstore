#!/usr/bin/env python3
"""detect os, distro, and hardware for package compatibility"""

import os
import platform
import re
import subprocess


def get_distro():
    """detect linux distribution"""
    info = {"name": "unknown", "id": "unknown", "version": ""}

    # try os-release first (most reliable)
    for path in ["/etc/os-release", "/usr/lib/os-release"]:
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("NAME="):
                        info["name"] = line.split("=", 1)[1].strip('"')
                    elif line.startswith("ID="):
                        info["id"] = line.split("=", 1)[1].strip('"')
                    elif line.startswith("VERSION_ID="):
                        info["version"] = line.split("=", 1)[1].strip('"')
            break

    return info


def get_package_manager():
    """detect available package manager"""
    managers = [
        ("pacman", "arch"),
        ("apt", "debian"),
        ("dnf", "fedora"),
        ("zypper", "opensuse"),
        ("apk", "alpine"),
        ("xbps-install", "void"),
        ("emerge", "gentoo"),
    ]

    for cmd, family in managers:
        try:
            result = subprocess.run(
                ["which", cmd], capture_output=True, timeout=5
            )
            if result.returncode == 0:
                return {"command": cmd, "family": family}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    return {"command": None, "family": "unknown"}


def get_hardware():
    """detect hardware info"""
    info = {
        "arch": platform.machine(),
        "cpu": "",
        "cores": os.cpu_count(),
        "ram_gb": 0,
        "gpu": [],
    }

    # cpu info
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("model name"):
                    info["cpu"] = line.split(":", 1)[1].strip()
                    break
    except FileNotFoundError:
        pass

    # ram
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    kb = int(re.search(r"\d+", line).group())
                    info["ram_gb"] = round(kb / 1024 / 1024, 1)
                    break
    except FileNotFoundError:
        pass

    # gpu detection
    try:
        result = subprocess.run(
            ["lspci"], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            if "VGA" in line or "3D" in line or "Display" in line:
                gpu_name = line.split(":", 2)[-1].strip()
                vendor = "unknown"
                if "NVIDIA" in line.upper() or "nvidia" in line:
                    vendor = "nvidia"
                elif "AMD" in line.upper() or "ATI" in line.upper():
                    vendor = "amd"
                elif "Intel" in line:
                    vendor = "intel"
                info["gpu"].append({"name": gpu_name, "vendor": vendor})
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return info


def get_install_command(package_name, pkg_manager):
    """get the right install command for the detected package manager"""
    commands = {
        "pacman": f"sudo pacman -S --noconfirm {package_name}",
        "apt": f"sudo apt install -y {package_name}",
        "dnf": f"sudo dnf install -y {package_name}",
        "zypper": f"sudo zypper install -y {package_name}",
        "apk": f"sudo apk add {package_name}",
        "xbps-install": f"sudo xbps-install -y {package_name}",
        "emerge": f"sudo emerge {package_name}",
    }
    return commands.get(pkg_manager, f"echo 'unknown package manager'")


def system_report():
    """generate a full system report"""
    distro = get_distro()
    pkg_mgr = get_package_manager()
    hw = get_hardware()

    return {
        "distro": distro,
        "package_manager": pkg_mgr,
        "hardware": hw,
        "kernel": platform.release(),
        "python": platform.python_version(),
    }


if __name__ == "__main__":
    report = system_report()
    print("system info:")
    print(f"  distro:   {report['distro']['name']} {report['distro']['version']}")
    print(f"  kernel:   {report['kernel']}")
    print(f"  arch:     {report['hardware']['arch']}")
    print(f"  cpu:      {report['hardware']['cpu']}")
    print(f"  cores:    {report['hardware']['cores']}")
    print(f"  ram:      {report['hardware']['ram_gb']} gb")
    print(f"  pkg mgr:  {report['package_manager']['command']}")
    for gpu in report["hardware"]["gpu"]:
        print(f"  gpu:      {gpu['name']} ({gpu['vendor']})")
