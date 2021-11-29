#!/usr/bin/env python3
"""auto-detect package manager for multi-distro support"""

import shutil
import subprocess


PACKAGE_MANAGERS = {
    "pacman": {
        "binary": "pacman",
        "install": ["pacman", "-S", "--noconfirm"],
        "remove": ["pacman", "-R", "--noconfirm"],
        "search": ["pacman", "-Ss"],
        "update": ["pacman", "-Syu", "--noconfirm"],
        "list": ["pacman", "-Q"],
        "distros": ["arch", "manjaro", "endeavouros"],
    },
    "apt": {
        "binary": "apt",
        "install": ["apt-get", "install", "-y"],
        "remove": ["apt-get", "remove", "-y"],
        "search": ["apt-cache", "search"],
        "update": ["apt-get", "update", "&&", "apt-get", "upgrade", "-y"],
        "list": ["dpkg", "-l"],
        "distros": ["ubuntu", "debian", "mint", "pop"],
    },
    "dnf": {
        "binary": "dnf",
        "install": ["dnf", "install", "-y"],
        "remove": ["dnf", "remove", "-y"],
        "search": ["dnf", "search"],
        "update": ["dnf", "upgrade", "-y"],
        "list": ["dnf", "list", "installed"],
        "distros": ["fedora", "rhel", "centos", "rocky"],
    },
    "zypper": {
        "binary": "zypper",
        "install": ["zypper", "install", "-y"],
        "remove": ["zypper", "remove", "-y"],
        "search": ["zypper", "search"],
        "update": ["zypper", "update", "-y"],
        "list": ["zypper", "packages", "--installed"],
        "distros": ["opensuse", "suse"],
    },
}


def detect_package_manager():
    """detect the system's package manager."""
    for name, info in PACKAGE_MANAGERS.items():
        if shutil.which(info["binary"]):
            return name
    return None


def get_distro_id():
    """get distribution id from os-release."""
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("ID="):
                    return line.strip().split("=")[1].strip('"')
    except OSError:
        pass
    return "unknown"


def run_pkg_command(action, package=None):
    """run a package manager command."""
    pm = detect_package_manager()
    if not pm:
        return {"error": "no package manager found"}
    cmd = list(PACKAGE_MANAGERS[pm][action])
    if package:
        cmd.append(package)
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
        }
    except (subprocess.TimeoutExpired, OSError) as e:
        return {"error": str(e)}


if __name__ == "__main__":
    pm = detect_package_manager()
    distro = get_distro_id()
    print(f"distro: {distro}")
    print(f"package manager: {pm or 'not found'}")
    if pm:
        info = PACKAGE_MANAGERS[pm]
        print(f"install cmd: {' '.join(info['install'])} <pkg>")
