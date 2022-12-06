#!/usr/bin/env python3
"""system update checker for all package managers"""

import subprocess


def check_apt_updates():
    """check for apt package updates."""
    try:
        subprocess.run(
            ["apt", "update"],
            capture_output=True, timeout=60,
        )
        result = subprocess.run(
            ["apt", "list", "--upgradable"],
            capture_output=True, text=True, timeout=30,
        )
        updates = []
        for line in result.stdout.strip().splitlines()[1:]:
            if "/" in line:
                name = line.split("/")[0]
                updates.append({"name": name, "source": "apt"})
        return updates
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def check_pacman_updates():
    """check for pacman package updates."""
    try:
        result = subprocess.run(
            ["checkupdates"],
            capture_output=True, text=True, timeout=30,
        )
        updates = []
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) >= 4:
                updates.append({
                    "name": parts[0],
                    "current": parts[1],
                    "new": parts[3],
                    "source": "pacman",
                })
        return updates
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def check_dnf_updates():
    """check for dnf package updates."""
    try:
        result = subprocess.run(
            ["dnf", "check-update", "-q"],
            capture_output=True, text=True, timeout=60,
        )
        updates = []
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) >= 2 and "." in parts[0]:
                name = parts[0].rsplit(".", 1)[0]
                updates.append({"name": name, "version": parts[1], "source": "dnf"})
        return updates
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def check_all_updates():
    """check all available package managers for updates."""
    all_updates = []
    checkers = [
        ("apt", check_apt_updates),
        ("pacman", check_pacman_updates),
        ("dnf", check_dnf_updates),
    ]
    for name, checker in checkers:
        updates = checker()
        if updates:
            all_updates.extend(updates)
    return all_updates


def format_update_summary(updates):
    """format update list into summary string."""
    if not updates:
        return "system is up to date"
    by_source = {}
    for u in updates:
        src = u.get("source", "unknown")
        by_source.setdefault(src, []).append(u)
    lines = [f"{len(updates)} updates available:"]
    for src, pkgs in sorted(by_source.items()):
        lines.append(f"  {src}: {len(pkgs)} packages")
    return "\n".join(lines)


if __name__ == "__main__":
    updates = check_all_updates()
    print(format_update_summary(updates))
