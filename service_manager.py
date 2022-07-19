#!/usr/bin/env python3
"""systemd service manager integration"""

import subprocess


def list_services(state=None):
    """list systemd services."""
    cmd = ["systemctl", "list-units", "--type=service", "--no-pager", "--plain"]
    if state:
        cmd.extend([f"--state={state}"])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        services = []
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) >= 4 and parts[0].endswith(".service"):
                services.append({
                    "name": parts[0].replace(".service", ""),
                    "load": parts[1],
                    "active": parts[2],
                    "sub": parts[3],
                })
        return services
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def service_status(name):
    """get status of a specific service."""
    try:
        result = subprocess.run(
            ["systemctl", "status", name, "--no-pager"],
            capture_output=True, text=True, timeout=10,
        )
        is_active = subprocess.run(
            ["systemctl", "is-active", name],
            capture_output=True, text=True, timeout=5,
        )
        is_enabled = subprocess.run(
            ["systemctl", "is-enabled", name],
            capture_output=True, text=True, timeout=5,
        )
        return {
            "name": name,
            "active": is_active.stdout.strip(),
            "enabled": is_enabled.stdout.strip(),
            "output": result.stdout,
        }
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {"name": name, "active": "unknown", "enabled": "unknown"}


def start_service(name):
    """start a systemd service."""
    try:
        result = subprocess.run(
            ["systemctl", "start", name],
            capture_output=True, timeout=15,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def stop_service(name):
    """stop a systemd service."""
    try:
        result = subprocess.run(
            ["systemctl", "stop", name],
            capture_output=True, timeout=15,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def restart_service(name):
    """restart a systemd service."""
    try:
        result = subprocess.run(
            ["systemctl", "restart", name],
            capture_output=True, timeout=15,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def enable_service(name):
    """enable a service to start on boot."""
    try:
        result = subprocess.run(
            ["systemctl", "enable", name],
            capture_output=True, timeout=15,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


if __name__ == "__main__":
    services = list_services("running")
    print(f"running services: {len(services)}")
    for s in services[:10]:
        print(f"  {s['name']:30s} {s['active']}")
