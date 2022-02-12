#!/usr/bin/env python3
"""fetch and display package release notes"""

import json
import os
from datetime import datetime


NOTES_CACHE = os.path.expanduser("~/.cache/linuxstore/notes")


def parse_changelog(changelog_text, limit=5):
    """parse debian-style changelog into structured entries."""
    entries = []
    current = None
    for line in changelog_text.split("\n"):
        if line and not line.startswith(" ") and "(" in line:
            if current:
                entries.append(current)
            parts = line.split("(")
            current = {
                "package": parts[0].strip(),
                "version": parts[1].split(")")[0] if len(parts) > 1 else "",
                "changes": [],
            }
        elif current and line.strip().startswith("*"):
            current["changes"].append(line.strip()[2:])
        elif current and line.strip().startswith("-"):
            current["changes"].append(line.strip()[2:])
    if current:
        entries.append(current)
    return entries[:limit]


def format_release_notes(entries):
    """format parsed changelog entries for display."""
    lines = []
    for entry in entries:
        lines.append(f"{entry['package']} ({entry['version']})")
        for change in entry["changes"]:
            lines.append(f"  - {change}")
        lines.append("")
    return "\n".join(lines)


def cache_notes(package_name, notes):
    """cache release notes locally."""
    os.makedirs(NOTES_CACHE, exist_ok=True)
    path = os.path.join(NOTES_CACHE, f"{package_name}.json")
    data = {
        "package": package_name,
        "cached_at": datetime.now().isoformat(),
        "notes": notes,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_cached_notes(package_name, max_age_hours=24):
    """load cached notes if fresh enough."""
    path = os.path.join(NOTES_CACHE, f"{package_name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        data = json.load(f)
    cached_at = datetime.fromisoformat(data["cached_at"])
    age_hours = (datetime.now() - cached_at).total_seconds() / 3600
    if age_hours > max_age_hours:
        return None
    return data["notes"]


if __name__ == "__main__":
    sample = """firefox (97.0-1)
  * updated to version 97.0
  - security fixes for CVE-2022-001
  - improved webrender performance

firefox (96.0-1)
  * updated to version 96.0
  - cookie policy improvements
"""
    entries = parse_changelog(sample)
    print(format_release_notes(entries))
