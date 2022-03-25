#!/usr/bin/env python3
"""backup and restore installed package lists"""

import json
import os
import subprocess
import time


def backup_installed(output_path=None):
    """backup list of installed packages to json."""
    if output_path is None:
        output_path = os.path.expanduser("~/.linuxstore/backup.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    packages = _get_installed_packages()
    backup = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "package_count": len(packages),
        "packages": packages,
    }
    with open(output_path, "w") as f:
        json.dump(backup, f, indent=2)
    return output_path


def restore_from_backup(backup_path):
    """restore packages from a backup file."""
    with open(backup_path) as f:
        backup = json.load(f)
    packages = backup.get("packages", [])
    results = {"installed": [], "failed": [], "skipped": []}
    for pkg in packages:
        name = pkg.get("name", "")
        if not name:
            continue
        if _is_installed(name):
            results["skipped"].append(name)
            continue
        success = _install_package(name)
        if success:
            results["installed"].append(name)
        else:
            results["failed"].append(name)
    return results


def _get_installed_packages():
    """get list of explicitly installed packages."""
    managers = [
        (["dpkg", "--get-selections"], _parse_dpkg),
        (["pacman", "-Qe"], _parse_pacman),
        (["rpm", "-qa", "--qf", "%{NAME}\n"], _parse_simple),
    ]
    for cmd, parser in managers:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                return parser(result.stdout)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return []


def _parse_dpkg(output):
    packages = []
    for line in output.strip().splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "install":
            packages.append({"name": parts[0], "manager": "apt"})
    return packages


def _parse_pacman(output):
    packages = []
    for line in output.strip().splitlines():
        parts = line.split()
        if parts:
            packages.append({
                "name": parts[0],
                "version": parts[1] if len(parts) > 1 else "",
                "manager": "pacman",
            })
    return packages


def _parse_simple(output):
    return [{"name": line.strip(), "manager": "rpm"}
            for line in output.strip().splitlines() if line.strip()]


def _is_installed(name):
    cmds = [
        ["dpkg", "-s", name],
        ["pacman", "-Qi", name],
        ["rpm", "-q", name],
    ]
    for cmd in cmds:
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return False


def _install_package(name):
    cmds = [
        ["apt", "install", "-y", name],
        ["pacman", "-S", "--noconfirm", name],
        ["dnf", "install", "-y", name],
    ]
    for cmd in cmds:
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return False


if __name__ == "__main__":
    packages = _get_installed_packages()
    print(f"installed packages: {len(packages)}")
    path = backup_installed("/tmp/linuxstore_backup.json")
    print(f"backed up to: {path}")
