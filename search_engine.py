#!/usr/bin/env python3
"""unified search across all package sources"""

import subprocess


def search_all(query):
    """search across all available package managers."""
    results = []
    searchers = [
        ("native", _search_native),
        ("flatpak", _search_flatpak),
        ("snap", _search_snap),
    ]
    for source, searcher in searchers:
        found = searcher(query)
        for pkg in found:
            pkg["source"] = source
        results.extend(found)
    return results


def _search_native(query):
    methods = [
        (["pacman", "-Ss", query], _parse_pacman_search),
        (["apt-cache", "search", query], _parse_apt_search),
        (["dnf", "search", query], _parse_dnf_search),
    ]
    for cmd, parser in methods:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0 and result.stdout.strip():
                return parser(result.stdout)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return []


def _parse_pacman_search(output):
    packages = []
    lines = output.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if "/" in line and not line.startswith(" "):
            parts = line.split()
            name = parts[0].split("/")[1] if "/" in parts[0] else parts[0]
            version = parts[1] if len(parts) > 1 else ""
            desc = lines[i + 1].strip() if i + 1 < len(lines) else ""
            packages.append({"name": name, "version": version, "description": desc})
            i += 2
        else:
            i += 1
    return packages


def _parse_apt_search(output):
    packages = []
    for line in output.strip().splitlines():
        parts = line.split(" - ", 1)
        if len(parts) >= 2:
            packages.append({"name": parts[0].strip(), "description": parts[1].strip()})
    return packages


def _parse_dnf_search(output):
    packages = []
    for line in output.strip().splitlines():
        if ":" in line and not line.startswith("="):
            parts = line.split(":", 1)
            name = parts[0].strip().split(".")[0]
            desc = parts[1].strip() if len(parts) > 1 else ""
            packages.append({"name": name, "description": desc})
    return packages


def _search_flatpak(query):
    try:
        result = subprocess.run(
            ["flatpak", "search", query],
            capture_output=True, text=True, timeout=15,
        )
        packages = []
        for line in result.stdout.strip().splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 3:
                packages.append({
                    "name": parts[0],
                    "description": parts[1],
                    "id": parts[2],
                })
        return packages
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def _search_snap(query):
    try:
        result = subprocess.run(
            ["snap", "find", query],
            capture_output=True, text=True, timeout=15,
        )
        packages = []
        for line in result.stdout.strip().splitlines()[1:]:
            parts = line.split(None, 4)
            if len(parts) >= 2:
                packages.append({
                    "name": parts[0],
                    "version": parts[1],
                    "description": parts[-1] if len(parts) > 2 else "",
                })
        return packages
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


if __name__ == "__main__":
    results = search_all("vim")
    print(f"search 'vim': {len(results)} results")
    for r in results[:10]:
        print(f"  [{r['source']:8s}] {r['name']:25s} {r.get('description', '')[:40]}")
