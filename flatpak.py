#!/usr/bin/env python3
"""flatpak package management integration"""

import subprocess


def is_available():
    """check if flatpak is installed."""
    try:
        subprocess.run(["flatpak", "--version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def list_installed():
    """list installed flatpak packages."""
    try:
        result = subprocess.run(
            ["flatpak", "list", "--app", "--columns=application,name,version"],
            capture_output=True, text=True, timeout=15,
        )
        packages = []
        for line in result.stdout.strip().splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                packages.append({
                    "id": parts[0],
                    "name": parts[1],
                    "version": parts[2] if len(parts) > 2 else "",
                })
        return packages
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def install(app_id, remote="flathub"):
    """install a flatpak package."""
    try:
        result = subprocess.run(
            ["flatpak", "install", "-y", remote, app_id],
            capture_output=True, text=True, timeout=300,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def uninstall(app_id):
    """remove a flatpak package."""
    try:
        result = subprocess.run(
            ["flatpak", "uninstall", "-y", app_id],
            capture_output=True, text=True, timeout=60,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def update_all():
    """update all flatpak packages."""
    try:
        result = subprocess.run(
            ["flatpak", "update", "-y"],
            capture_output=True, text=True, timeout=600,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def search(query):
    """search for flatpak packages."""
    try:
        result = subprocess.run(
            ["flatpak", "search", query],
            capture_output=True, text=True, timeout=15,
        )
        results = []
        for line in result.stdout.strip().splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 3:
                results.append({
                    "name": parts[0],
                    "description": parts[1],
                    "id": parts[2],
                })
        return results
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def list_remotes():
    """list configured flatpak remotes."""
    try:
        result = subprocess.run(
            ["flatpak", "remotes", "--columns=name,url"],
            capture_output=True, text=True, timeout=10,
        )
        remotes = []
        for line in result.stdout.strip().splitlines():
            parts = line.split("\t")
            if parts:
                remotes.append({"name": parts[0], "url": parts[1] if len(parts) > 1 else ""})
        return remotes
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


if __name__ == "__main__":
    print(f"flatpak available: {is_available()}")
    if is_available():
        installed = list_installed()
        print(f"installed: {len(installed)}")
        for pkg in installed[:5]:
            print(f"  {pkg['name']} ({pkg['id']})")
