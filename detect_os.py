#!/usr/bin/env python3
"""detect os, distro, and hardware for package compatibility"""

import os
import platform
import re
import subprocess

PLATFORM = platform.system().lower()


def get_distro():
    """detect operating system and distribution"""
    info = {"name": "unknown", "id": "unknown", "version": ""}

    if PLATFORM == "darwin":
        info["name"] = "macOS"
        info["id"] = "macos"
        try:
            result = subprocess.run(
                ["sw_vers", "-productVersion"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                info["version"] = result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            info["version"] = platform.mac_ver()[0]
        return info

    if PLATFORM == "windows":
        info["name"] = "Windows"
        info["id"] = "windows"
        info["version"] = platform.version()
        return info

    # linux - try os-release first
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


def _cmd_exists(cmd):
    """check if a command exists on the system"""
    check = "where" if PLATFORM == "windows" else "which"
    try:
        result = subprocess.run(
            [check, cmd], capture_output=True, timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_package_manager():
    """detect available package manager"""
    if PLATFORM == "darwin":
        if _cmd_exists("brew"):
            return {"command": "brew", "family": "macos"}
        return {"command": None, "family": "macos"}

    if PLATFORM == "windows":
        for cmd, name in [("winget", "winget"), ("choco", "chocolatey")]:
            if _cmd_exists(cmd):
                return {"command": cmd, "family": name}
        return {"command": None, "family": "windows"}

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
        if _cmd_exists(cmd):
            return {"command": cmd, "family": family}

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
    if PLATFORM == "darwin":
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                info["cpu"] = result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    elif PLATFORM == "windows":
        info["cpu"] = platform.processor() or "unknown"
    else:
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("model name"):
                        info["cpu"] = line.split(":", 1)[1].strip()
                        break
        except FileNotFoundError:
            pass

    # ram
    if PLATFORM == "darwin":
        try:
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                info["ram_gb"] = round(int(result.stdout.strip()) / 1024**3, 1)
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass
    elif PLATFORM == "windows":
        try:
            result = subprocess.run(
                ["wmic", "computersystem", "get", "totalphysicalmemory"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if line.isdigit():
                    info["ram_gb"] = round(int(line) / 1024**3, 1)
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass
    else:
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
    if PLATFORM != "windows":
        try:
            cmd = ["system_profiler", "SPDisplaysDataType"] if PLATFORM == "darwin" else ["lspci"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            for line in result.stdout.split("\n"):
                if PLATFORM == "darwin":
                    if "Chipset Model" in line:
                        gpu_name = line.split(":", 1)[1].strip()
                        info["gpu"].append({"name": gpu_name, "vendor": "apple"})
                else:
                    if "VGA" in line or "3D" in line or "Display" in line:
                        gpu_name = line.split(":", 2)[-1].strip()
                        vendor = "unknown"
                        if "NVIDIA" in line.upper():
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
    return commands.get(pkg_manager, "echo 'unknown package manager'")


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
