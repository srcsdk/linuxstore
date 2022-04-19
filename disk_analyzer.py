#!/usr/bin/env python3
"""analyze disk usage by installed packages"""

import subprocess
import os


def package_sizes():
    """get sizes of installed packages."""
    methods = [
        _pacman_sizes,
        _dpkg_sizes,
        _rpm_sizes,
    ]
    for method in methods:
        sizes = method()
        if sizes:
            return sizes
    return []


def _pacman_sizes():
    try:
        result = subprocess.run(
            ["pacman", "-Qi"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return []
        packages = []
        current = {}
        for line in result.stdout.splitlines():
            if line.startswith("Name"):
                current["name"] = line.split(":", 1)[1].strip()
            elif line.startswith("Installed Size"):
                size_str = line.split(":", 1)[1].strip()
                current["size"] = _parse_size(size_str)
                current["size_str"] = size_str
                packages.append(dict(current))
                current = {}
        packages.sort(key=lambda p: p.get("size", 0), reverse=True)
        return packages
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def _dpkg_sizes():
    try:
        result = subprocess.run(
            ["dpkg-query", "-W", "-f=${Package}\t${Installed-Size}\n"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return []
        packages = []
        for line in result.stdout.strip().splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                try:
                    size_kb = int(parts[1])
                except ValueError:
                    continue
                packages.append({
                    "name": parts[0],
                    "size": size_kb * 1024,
                    "size_str": f"{size_kb} KiB",
                })
        packages.sort(key=lambda p: p["size"], reverse=True)
        return packages
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def _rpm_sizes():
    try:
        result = subprocess.run(
            ["rpm", "-qa", "--qf", "%{NAME}\t%{SIZE}\n"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return []
        packages = []
        for line in result.stdout.strip().splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                try:
                    size = int(parts[1])
                except ValueError:
                    continue
                packages.append({
                    "name": parts[0],
                    "size": size,
                    "size_str": _format_size(size),
                })
        packages.sort(key=lambda p: p["size"], reverse=True)
        return packages
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def _parse_size(size_str):
    parts = size_str.split()
    if len(parts) < 2:
        return 0
    try:
        val = float(parts[0])
    except ValueError:
        return 0
    unit = parts[1].lower()
    multipliers = {"b": 1, "kib": 1024, "mib": 1024**2, "gib": 1024**3}
    return int(val * multipliers.get(unit, 1))


def _format_size(size_bytes):
    if size_bytes >= 1024**3:
        return f"{size_bytes / 1024**3:.1f} GiB"
    if size_bytes >= 1024**2:
        return f"{size_bytes / 1024**2:.1f} MiB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KiB"
    return f"{size_bytes} B"


def top_packages(n=20):
    """get top n largest packages."""
    sizes = package_sizes()
    return sizes[:n]


def total_disk_usage():
    """total disk used by all packages."""
    sizes = package_sizes()
    total = sum(p.get("size", 0) for p in sizes)
    return {"total_bytes": total, "total_str": _format_size(total), "package_count": len(sizes)}


if __name__ == "__main__":
    usage = total_disk_usage()
    print(f"total package disk usage: {usage['total_str']}")
    print(f"packages: {usage['package_count']}")
    print("\nlargest packages:")
    for pkg in top_packages(10):
        print(f"  {pkg['name']:30s} {pkg.get('size_str', '')}")
