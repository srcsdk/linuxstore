#!/usr/bin/env python3
"""check for available package updates"""

import subprocess
import re


def check_apt_updates():
    """check for available apt updates."""
    try:
        output = subprocess.check_output(
            ["apt", "list", "--upgradable"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        updates = []
        for line in output.splitlines():
            if "/" in line and "upgradable" in line.lower():
                parts = line.split("/")
                name = parts[0]
                version_match = re.search(r"(\S+)\s+\[", line)
                version = version_match.group(1) if version_match else ""
                updates.append({"name": name, "version": version})
        return updates
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def check_pacman_updates():
    """check for available pacman updates."""
    try:
        output = subprocess.check_output(
            ["checkupdates"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        updates = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 4:
                updates.append({
                    "name": parts[0],
                    "current": parts[1],
                    "new": parts[3],
                })
        return updates
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def check_dnf_updates():
    """check for available dnf updates."""
    try:
        output = subprocess.check_output(
            ["dnf", "check-update", "--quiet"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        updates = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 3 and "." in parts[0]:
                name = parts[0].rsplit(".", 1)[0]
                updates.append({"name": name, "version": parts[1]})
        return updates
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def check_updates(package_manager=None):
    """check for updates using detected or specified package manager."""
    checkers = {
        "apt": check_apt_updates,
        "pacman": check_pacman_updates,
        "dnf": check_dnf_updates,
    }
    if package_manager and package_manager in checkers:
        return checkers[package_manager]()
    for name, checker in checkers.items():
        result = checker()
        if result:
            return result
    return []


def format_updates(updates, limit=20):
    """format update list for display."""
    lines = [f"{len(updates)} updates available:"]
    for update in updates[:limit]:
        name = update.get("name", "unknown")
        version = update.get("version", update.get("new", ""))
        lines.append(f"  {name} -> {version}")
    if len(updates) > limit:
        lines.append(f"  ... and {len(updates) - limit} more")
    return "\n".join(lines)


if __name__ == "__main__":
    updates = check_updates()
    if updates:
        print(format_updates(updates))
    else:
        print("no updates available (or package manager not found)")
