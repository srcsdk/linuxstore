#!/usr/bin/env python3
"""system information gathering for package management"""

import os
import platform


def cpu_info():
    """get cpu information."""
    info = {"cores": os.cpu_count() or 0, "arch": platform.machine()}
    if os.path.isfile("/proc/cpuinfo"):
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    info["model"] = line.split(":")[1].strip()
                    break
    return info


def memory_info():
    """get memory information."""
    info = {}
    if os.path.isfile("/proc/meminfo"):
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    kb = int(line.split()[1])
                    info["total_mb"] = round(kb / 1024)
                elif line.startswith("MemAvailable"):
                    kb = int(line.split()[1])
                    info["available_mb"] = round(kb / 1024)
    return info


def disk_info():
    """get disk usage information."""
    try:
        stat = os.statvfs("/")
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bavail * stat.f_frsize
        return {
            "total_gb": round(total / (1024 ** 3), 1),
            "free_gb": round(free / (1024 ** 3), 1),
            "used_pct": round((1 - free / total) * 100, 1),
        }
    except OSError:
        return {}


def uptime():
    """get system uptime."""
    if os.path.isfile("/proc/uptime"):
        with open("/proc/uptime") as f:
            seconds = float(f.read().split()[0])
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        return f"{days}d {hours}h"
    return "unknown"


def system_summary():
    """get complete system summary."""
    return {
        "hostname": platform.node(),
        "os": platform.system(),
        "kernel": platform.release(),
        "arch": platform.machine(),
        "python": platform.python_version(),
        "cpu": cpu_info(),
        "memory": memory_info(),
        "disk": disk_info(),
        "uptime": uptime(),
    }


if __name__ == "__main__":
    info = system_summary()
    print("system information:")
    for key, value in info.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
