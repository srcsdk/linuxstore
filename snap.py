#!/usr/bin/env python3
"""snap package management integration"""

import subprocess
import json


def is_available():
    """check if snap is installed."""
    try:
        subprocess.run(["snap", "version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def list_installed():
    """list installed snap packages."""
    try:
        result = subprocess.run(
            ["snap", "list"],
            capture_output=True, text=True, timeout=15,
        )
        packages = []
        for line in result.stdout.strip().splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 4:
                packages.append({
                    "name": parts[0],
                    "version": parts[1],
                    "rev": parts[2],
                    "channel": parts[3],
                })
        return packages
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def install(name, channel="stable", classic=False):
    """install a snap package."""
    cmd = ["snap", "install", name, f"--channel={channel}"]
    if classic:
        cmd.append("--classic")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def remove(name):
    """remove a snap package."""
    try:
        result = subprocess.run(
            ["snap", "remove", name],
            capture_output=True, text=True, timeout=60,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def search(query):
    """search for snap packages."""
    try:
        result = subprocess.run(
            ["snap", "find", query],
            capture_output=True, text=True, timeout=15,
        )
        results = []
        for line in result.stdout.strip().splitlines()[1:]:
            parts = line.split(None, 4)
            if len(parts) >= 2:
                results.append({
                    "name": parts[0],
                    "version": parts[1],
                    "summary": parts[-1] if len(parts) > 2 else "",
                })
        return results
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def refresh_all():
    """update all snap packages."""
    try:
        result = subprocess.run(
            ["snap", "refresh"],
            capture_output=True, text=True, timeout=600,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def info(name):
    """get detailed info about a snap."""
    try:
        result = subprocess.run(
            ["snap", "info", name],
            capture_output=True, text=True, timeout=15,
        )
        info_dict = {}
        for line in result.stdout.strip().splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                info_dict[key.strip().lower()] = val.strip()
        return info_dict
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {}


if __name__ == "__main__":
    print(f"snap available: {is_available()}")
    if is_available():
        installed = list_installed()
        print(f"installed: {len(installed)}")
        for pkg in installed[:5]:
            print(f"  {pkg['name']} {pkg['version']}")
