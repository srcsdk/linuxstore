#!/usr/bin/env python3
"""flatpak and snap integration with unified search"""

import subprocess
import shutil


def has_flatpak():
    """check if flatpak is installed."""
    return shutil.which("flatpak") is not None


def has_snap():
    """check if snap is installed."""
    return shutil.which("snap") is not None


def search_flatpak(query):
    """search flatpak for packages."""
    if not has_flatpak():
        return []
    try:
        result = subprocess.run(
            ["flatpak", "search", query],
            capture_output=True, text=True, timeout=15,
        )
        packages = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                packages.append({
                    "name": parts[0].strip(),
                    "description": parts[1].strip() if len(parts) > 1 else "",
                    "source": "flatpak",
                    "id": parts[2].strip() if len(parts) > 2 else "",
                })
        return packages
    except (subprocess.TimeoutExpired, OSError):
        return []


def search_snap(query):
    """search snap store for packages."""
    if not has_snap():
        return []
    try:
        result = subprocess.run(
            ["snap", "find", query],
            capture_output=True, text=True, timeout=15,
        )
        packages = []
        for line in result.stdout.strip().split("\n")[1:]:
            parts = line.split()
            if len(parts) >= 2:
                packages.append({
                    "name": parts[0],
                    "version": parts[1] if len(parts) > 1 else "",
                    "source": "snap",
                })
        return packages
    except (subprocess.TimeoutExpired, OSError):
        return []


def unified_search(query):
    """search across all available package sources."""
    results = []
    results.extend(search_flatpak(query))
    results.extend(search_snap(query))
    return results


def install_universal(package_id, source):
    """install package from specified source."""
    if source == "flatpak":
        cmd = ["flatpak", "install", "-y", package_id]
    elif source == "snap":
        cmd = ["snap", "install", package_id]
    else:
        return {"error": f"unknown source: {source}"}
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
        )
        return {"success": result.returncode == 0, "output": result.stdout}
    except (subprocess.TimeoutExpired, OSError) as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print(f"flatpak available: {has_flatpak()}")
    print(f"snap available: {has_snap()}")
    import sys
    if len(sys.argv) > 1:
        results = unified_search(sys.argv[1])
        print(f"found {len(results)} packages")
        for r in results:
            print(f"  [{r['source']}] {r['name']}")
