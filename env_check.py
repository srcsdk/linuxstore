#!/usr/bin/env python3
"""environment compatibility checker"""

import os
import subprocess
import platform


def check_desktop_environment():
    """detect current desktop environment."""
    de = os.environ.get("XDG_CURRENT_DESKTOP", "")
    session = os.environ.get("DESKTOP_SESSION", "")
    wayland = os.environ.get("WAYLAND_DISPLAY", "")
    return {
        "desktop": de or session or "unknown",
        "display_server": "wayland" if wayland else "x11",
        "session_type": os.environ.get("XDG_SESSION_TYPE", "unknown"),
    }


def check_display_server():
    """check display server details."""
    info = {"type": "unknown", "version": ""}
    wayland = os.environ.get("WAYLAND_DISPLAY")
    if wayland:
        info["type"] = "wayland"
        info["socket"] = wayland
    else:
        display = os.environ.get("DISPLAY")
        if display:
            info["type"] = "x11"
            info["display"] = display
    return info


def check_init_system():
    """detect init system."""
    if os.path.isdir("/run/systemd/system"):
        return "systemd"
    try:
        with open("/proc/1/comm") as f:
            init = f.read().strip()
            return init
    except OSError:
        return "unknown"


def check_package_managers():
    """detect available package managers."""
    managers = {
        "apt": "apt",
        "pacman": "pacman",
        "dnf": "dnf",
        "zypper": "zypper",
        "emerge": "emerge",
        "xbps-install": "xbps",
        "flatpak": "flatpak",
        "snap": "snap",
    }
    available = []
    for cmd, name in managers.items():
        try:
            subprocess.run(
                ["which", cmd],
                capture_output=True, timeout=5,
            )
            available.append(name)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return available


def full_compatibility_check():
    """run full environment compatibility check."""
    return {
        "platform": platform.system(),
        "distro": _detect_distro(),
        "kernel": platform.release(),
        "arch": platform.machine(),
        "python": platform.python_version(),
        "desktop": check_desktop_environment(),
        "display": check_display_server(),
        "init": check_init_system(),
        "package_managers": check_package_managers(),
    }


def _detect_distro():
    """detect linux distribution."""
    try:
        with open("/etc/os-release") as f:
            info = {}
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    info[key] = val.strip('"')
            return info.get("PRETTY_NAME", info.get("NAME", "unknown"))
    except OSError:
        return "unknown"


if __name__ == "__main__":
    compat = full_compatibility_check()
    print(f"distro: {compat['distro']}")
    print(f"kernel: {compat['kernel']} ({compat['arch']})")
    print(f"desktop: {compat['desktop']['desktop']}")
    print(f"display: {compat['display']['type']}")
    print(f"init: {compat['init']}")
    print(f"package managers: {', '.join(compat['package_managers'])}")
