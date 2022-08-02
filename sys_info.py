#!/usr/bin/env python3
"""detailed system information display"""

import os
import platform
import subprocess


def cpu_info():
    """get cpu information."""
    info = {"model": "", "cores": os.cpu_count() or 0, "threads": 0}
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    info["model"] = line.split(":", 1)[1].strip()
                elif line.startswith("processor"):
                    info["threads"] = int(line.split(":", 1)[1].strip()) + 1
    except (OSError, ValueError):
        pass
    return info


def memory_info():
    """get memory information."""
    info = {"total": 0, "available": 0, "used": 0}
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                parts = line.split()
                if parts[0] == "MemTotal:":
                    info["total"] = int(parts[1]) * 1024
                elif parts[0] == "MemAvailable:":
                    info["available"] = int(parts[1]) * 1024
    except (OSError, ValueError, IndexError):
        pass
    info["used"] = info["total"] - info["available"]
    return info


def disk_info():
    """get disk partition info."""
    partitions = []
    try:
        result = subprocess.run(
            ["df", "-h", "--output=source,size,used,avail,pcent,target"],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.strip().splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 6 and parts[0].startswith("/"):
                partitions.append({
                    "device": parts[0],
                    "size": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "percent": parts[4],
                    "mount": parts[5],
                })
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return partitions


def gpu_info():
    """detect gpu information."""
    gpus = []
    try:
        result = subprocess.run(
            ["lspci", "-v"],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.splitlines():
            lower = line.lower()
            if "vga" in lower or "3d" in lower or "display" in lower:
                gpus.append(line.strip().split(": ", 1)[-1])
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return gpus


def system_summary():
    """generate full system summary."""
    cpu = cpu_info()
    mem = memory_info()
    disks = disk_info()
    gpus = gpu_info()
    return {
        "hostname": platform.node(),
        "os": platform.system(),
        "kernel": platform.release(),
        "arch": platform.machine(),
        "cpu": cpu,
        "memory_gb": round(mem["total"] / (1024**3), 1),
        "memory_used_gb": round(mem["used"] / (1024**3), 1),
        "disks": len(disks),
        "gpus": gpus,
    }


if __name__ == "__main__":
    info = system_summary()
    print(f"hostname: {info['hostname']}")
    print(f"os: {info['os']} {info['kernel']} ({info['arch']})")
    print(f"cpu: {info['cpu']['model']}")
    print(f"cores: {info['cpu']['cores']}, threads: {info['cpu']['threads']}")
    print(f"memory: {info['memory_used_gb']}/{info['memory_gb']} GB")
    print(f"disks: {info['disks']}")
    for gpu in info["gpus"]:
        print(f"gpu: {gpu}")
