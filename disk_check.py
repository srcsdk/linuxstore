#!/usr/bin/env python3
"""package size estimation and disk space check"""

import os
import shutil


def get_disk_usage(path="/"):
    """get disk usage for a mount point."""
    usage = shutil.disk_usage(path)
    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "used_pct": round(usage.used / usage.total * 100, 1),
    }


def format_bytes(size):
    """format byte count to human readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size) < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def check_space(required_bytes, path="/"):
    """check if enough disk space is available."""
    usage = get_disk_usage(path)
    has_space = usage["free"] >= required_bytes
    return {
        "sufficient": has_space,
        "required": format_bytes(required_bytes),
        "available": format_bytes(usage["free"]),
        "after_install": format_bytes(usage["free"] - required_bytes)
        if has_space else "insufficient",
    }


def estimate_package_size(package_info):
    """estimate installed size from package metadata."""
    download = package_info.get("download_size", 0)
    installed = package_info.get("installed_size", 0)
    if installed > 0:
        return installed
    return int(download * 3)


def dir_size(path):
    """calculate total size of a directory."""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total


if __name__ == "__main__":
    usage = get_disk_usage("/")
    print("disk usage:")
    print(f"  total: {format_bytes(usage['total'])}")
    print(f"  used:  {format_bytes(usage['used'])} ({usage['used_pct']}%)")
    print(f"  free:  {format_bytes(usage['free'])}")
    check = check_space(500 * 1024 * 1024)
    print(f"500mb install: {check['sufficient']}")
