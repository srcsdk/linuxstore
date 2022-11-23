#!/usr/bin/env python3
"""hardware driver detection and management"""

import subprocess
import os


def detect_hardware():
    """detect hardware that may need drivers."""
    devices = []
    try:
        result = subprocess.run(
            ["lspci", "-nn"],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.strip().splitlines():
            lower = line.lower()
            if any(kw in lower for kw in ["vga", "3d", "network", "wireless", "audio"]):
                devices.append({
                    "description": line.strip(),
                    "type": _classify_device(lower),
                })
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return devices


def _classify_device(desc):
    if "vga" in desc or "3d" in desc:
        return "gpu"
    if "network" in desc or "wireless" in desc or "wifi" in desc:
        return "network"
    if "audio" in desc:
        return "audio"
    return "other"


def list_loaded_modules():
    """list currently loaded kernel modules."""
    try:
        result = subprocess.run(
            ["lsmod"],
            capture_output=True, text=True, timeout=10,
        )
        modules = []
        for line in result.stdout.strip().splitlines()[1:]:
            parts = line.split()
            if parts:
                modules.append({
                    "name": parts[0],
                    "size": int(parts[1]) if len(parts) > 1 else 0,
                    "used_by": parts[3].split(",") if len(parts) > 3 else [],
                })
        return modules
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def check_nvidia():
    """check nvidia driver status."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(",")
            return {
                "installed": True,
                "gpu": parts[0].strip() if parts else "",
                "driver": parts[1].strip() if len(parts) > 1 else "",
            }
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return {"installed": False}


def driver_summary():
    """get driver status summary."""
    devices = detect_hardware()
    modules = list_loaded_modules()
    nvidia = check_nvidia()
    gpu_modules = [m for m in modules if any(
        kw in m["name"] for kw in ["nvidia", "amdgpu", "radeon", "i915", "nouveau"]
    )]
    return {
        "hardware_devices": len(devices),
        "loaded_modules": len(modules),
        "gpu_drivers": [m["name"] for m in gpu_modules],
        "nvidia": nvidia,
    }


if __name__ == "__main__":
    summary = driver_summary()
    print(f"detected devices: {summary['hardware_devices']}")
    print(f"loaded modules: {summary['loaded_modules']}")
    print(f"gpu drivers: {', '.join(summary['gpu_drivers']) or 'none detected'}")
    if summary["nvidia"]["installed"]:
        print(f"nvidia: {summary['nvidia']['gpu']} (driver {summary['nvidia']['driver']})")
