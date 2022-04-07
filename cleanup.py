#!/usr/bin/env python3
"""system cleanup: remove orphaned packages and clear caches"""

import subprocess
import os


def find_orphans():
    """find orphaned packages with no dependents."""
    methods = [
        (["pacman", "-Qtdq"], "pacman"),
        (["deborphan"], "apt"),
    ]
    for cmd, mgr in methods:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                names = [l.strip() for l in result.stdout.splitlines() if l.strip()]
                return [{"name": n, "manager": mgr} for n in names]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return []


def remove_orphans():
    """remove orphaned packages."""
    orphans = find_orphans()
    if not orphans:
        return {"removed": 0}
    names = [o["name"] for o in orphans]
    mgr = orphans[0]["manager"]
    if mgr == "pacman":
        cmd = ["pacman", "-Rns", "--noconfirm"] + names
    elif mgr == "apt":
        cmd = ["apt", "autoremove", "-y"]
    else:
        return {"removed": 0}
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        return {"removed": len(names) if result.returncode == 0 else 0}
    except subprocess.TimeoutExpired:
        return {"removed": 0}


def cache_size():
    """get package cache size."""
    cache_dirs = [
        "/var/cache/pacman/pkg",
        "/var/cache/apt/archives",
        "/var/cache/dnf",
    ]
    total = 0
    for d in cache_dirs:
        if os.path.isdir(d):
            for root, dirs, files in os.walk(d):
                for f in files:
                    total += os.path.getsize(os.path.join(root, f))
    return total


def clear_cache():
    """clear package manager caches."""
    cmds = [
        ["pacman", "-Sc", "--noconfirm"],
        ["apt", "clean"],
        ["dnf", "clean", "all"],
    ]
    cleared = False
    for cmd in cmds:
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode == 0:
                cleared = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return cleared


def cleanup_summary():
    """generate cleanup summary."""
    orphans = find_orphans()
    cache = cache_size()
    return {
        "orphaned_packages": len(orphans),
        "cache_size_mb": round(cache / (1024 * 1024), 1),
        "orphan_names": [o["name"] for o in orphans[:10]],
    }


if __name__ == "__main__":
    summary = cleanup_summary()
    print(f"orphaned packages: {summary['orphaned_packages']}")
    print(f"cache size: {summary['cache_size_mb']} MB")
    if summary["orphan_names"]:
        for name in summary["orphan_names"]:
            print(f"  orphan: {name}")
