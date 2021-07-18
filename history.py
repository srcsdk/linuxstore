#!/usr/bin/env python3
"""package action history log"""

import json
import time
from pathlib import Path

HISTORY_DIR = Path.home() / ".config" / "linuxstore"
HISTORY_FILE = HISTORY_DIR / "history.json"
MAX_ENTRIES = 500


def load_history():
    """load action history from disk"""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_history(entries):
    """save history entries to disk"""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    # keep only the most recent entries
    entries = entries[-MAX_ENTRIES:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def log_action(action, package_name, success=True, details=""):
    """log a package action (install, uninstall, update)"""
    entries = load_history()
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "package": package_name,
        "success": success,
        "details": details,
    }
    entries.append(entry)
    save_history(entries)
    return entry


def get_recent(limit=50):
    """get most recent history entries"""
    entries = load_history()
    return entries[-limit:][::-1]


def get_by_package(package_name):
    """get all history entries for a specific package"""
    entries = load_history()
    return [e for e in entries if e["package"] == package_name]


def get_by_action(action):
    """get all history entries for a specific action type"""
    entries = load_history()
    return [e for e in entries if e["action"] == action]


def clear_history():
    """clear all history entries"""
    save_history([])


def format_history(entries, limit=20):
    """format history entries for display"""
    lines = []
    for entry in entries[:limit]:
        status = "ok" if entry["success"] else "fail"
        lines.append(
            f"  [{entry['timestamp']}] {entry['action']:<10} "
            f"{entry['package']:<25} {status}"
        )
    return "\n".join(lines)


def get_changelog(package_name):
    """return changelog entries for a package based on its action history.

    formats history entries into a changelog-style list of dicts.
    """
    entries = get_by_package(package_name)
    if not entries:
        return []

    changelog = []
    for entry in reversed(entries):
        changelog.append({
            "date": entry.get("timestamp", ""),
            "action": entry.get("action", ""),
            "success": entry.get("success", False),
            "details": entry.get("details", ""),
        })
    return changelog


def stats():
    """get history statistics"""
    entries = load_history()
    total = len(entries)
    installs = sum(1 for e in entries if e["action"] == "install")
    uninstalls = sum(1 for e in entries if e["action"] == "uninstall")
    updates = sum(1 for e in entries if e["action"] == "update")
    failures = sum(1 for e in entries if not e["success"])
    return {
        "total_actions": total,
        "installs": installs,
        "uninstalls": uninstalls,
        "updates": updates,
        "failures": failures,
    }
