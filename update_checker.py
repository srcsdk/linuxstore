#!/usr/bin/env python3
"""package update checker with version comparison"""

import re
import subprocess


def parse_version(version_str):
    """parse version string into comparable tuple."""
    parts = re.findall(r"\d+", version_str)
    return tuple(int(p) for p in parts) if parts else (0,)


def compare_versions(v1, v2):
    """compare two version strings.

    returns: -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    """
    t1 = parse_version(v1)
    t2 = parse_version(v2)
    if t1 < t2:
        return -1
    elif t1 > t2:
        return 1
    return 0


def check_updates_pacman():
    """check for available updates using pacman."""
    try:
        result = subprocess.run(
            ["pacman", "-Qu"],
            capture_output=True, text=True, timeout=30,
        )
        updates = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                updates.append({
                    "package": parts[0],
                    "current": parts[1],
                    "available": parts[3],
                })
        return updates
    except (subprocess.TimeoutExpired, OSError):
        return []


def check_updates_apt():
    """check for available updates using apt."""
    try:
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True, timeout=60,
        )
        result = subprocess.run(
            ["apt", "list", "--upgradable"],
            capture_output=True, text=True, timeout=30,
        )
        updates = []
        for line in result.stdout.strip().split("\n"):
            if "/" not in line:
                continue
            name = line.split("/")[0]
            version_match = re.search(r"(\S+)\s+\[.*?:\s*(\S+)", line)
            if version_match:
                updates.append({
                    "package": name,
                    "available": version_match.group(1),
                    "current": version_match.group(2),
                })
        return updates
    except (subprocess.TimeoutExpired, OSError):
        return []


def format_updates(updates):
    """format update list for display."""
    if not updates:
        return "all packages up to date"
    lines = [f"  {len(updates)} updates available:"]
    for u in updates:
        lines.append(
            f"    {u['package']}: {u['current']} -> {u['available']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print("checking for updates...")
    updates = check_updates_pacman()
    if not updates:
        updates = check_updates_apt()
    print(format_updates(updates))
