#!/usr/bin/env python3
"""log viewer for package install and update history"""

import subprocess
import os
import re
from datetime import datetime


def get_install_history(limit=50):
    """get package install/update history."""
    methods = [_pacman_log, _apt_log, _dnf_log]
    for method in methods:
        entries = method(limit)
        if entries:
            return entries
    return []


def _pacman_log(limit):
    log_path = "/var/log/pacman.log"
    if not os.path.isfile(log_path):
        return []
    entries = []
    pattern = re.compile(
        r"\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}).*\] "
        r"\[ALPM\] (installed|upgraded|removed) (.+)"
    )
    try:
        with open(log_path) as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    entries.append({
                        "timestamp": match.group(1),
                        "action": match.group(2),
                        "package": match.group(3).split()[0],
                        "detail": match.group(3),
                    })
    except PermissionError:
        return []
    entries.reverse()
    return entries[:limit]


def _apt_log(limit):
    log_path = "/var/log/apt/history.log"
    if not os.path.isfile(log_path):
        return []
    entries = []
    try:
        with open(log_path) as f:
            current = {}
            for line in f:
                line = line.strip()
                if line.startswith("Start-Date:"):
                    current = {"timestamp": line.split(":", 1)[1].strip()}
                elif line.startswith("Commandline:"):
                    current["command"] = line.split(":", 1)[1].strip()
                elif line.startswith("Install:"):
                    pkgs = line.split(":", 1)[1].strip()
                    for pkg in pkgs.split(","):
                        name = pkg.strip().split(":")[0].split("(")[0].strip()
                        entries.append({
                            "timestamp": current.get("timestamp", ""),
                            "action": "installed",
                            "package": name,
                        })
                elif line.startswith("Upgrade:"):
                    pkgs = line.split(":", 1)[1].strip()
                    for pkg in pkgs.split(","):
                        name = pkg.strip().split(":")[0].split("(")[0].strip()
                        entries.append({
                            "timestamp": current.get("timestamp", ""),
                            "action": "upgraded",
                            "package": name,
                        })
                elif line.startswith("Remove:"):
                    pkgs = line.split(":", 1)[1].strip()
                    for pkg in pkgs.split(","):
                        name = pkg.strip().split(":")[0].split("(")[0].strip()
                        entries.append({
                            "timestamp": current.get("timestamp", ""),
                            "action": "removed",
                            "package": name,
                        })
    except PermissionError:
        return []
    entries.reverse()
    return entries[:limit]


def _dnf_log(limit):
    try:
        result = subprocess.run(
            ["dnf", "history", "list"],
            capture_output=True, text=True, timeout=15,
        )
        entries = []
        for line in result.stdout.strip().splitlines()[2:]:
            parts = line.split("|")
            if len(parts) >= 4:
                entries.append({
                    "id": parts[0].strip(),
                    "action": parts[2].strip(),
                    "timestamp": parts[1].strip(),
                })
        return entries[:limit]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def format_history(entries):
    """format history entries for display."""
    lines = []
    for e in entries:
        ts = e.get("timestamp", "")[:19]
        action = e.get("action", "")
        pkg = e.get("package", e.get("detail", ""))
        lines.append(f"{ts}  {action:10s}  {pkg}")
    return "\n".join(lines)


if __name__ == "__main__":
    history = get_install_history(20)
    print(f"recent history ({len(history)} entries):")
    print(format_history(history))
