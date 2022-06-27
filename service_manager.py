#!/usr/bin/env python3
"""system service management utilities"""

import subprocess


def list_services(active_only=False):
    """list systemd services."""
    cmd = ["systemctl", "list-units", "--type=service", "--no-pager"]
    if active_only:
        cmd.append("--state=active")
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL, text=True,
        )
        services = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 4 and parts[0].endswith(".service"):
                services.append({
                    "name": parts[0],
                    "load": parts[1],
                    "active": parts[2],
                    "sub": parts[3],
                })
        return services
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def service_status(name):
    """get detailed status of a service."""
    try:
        output = subprocess.check_output(
            ["systemctl", "status", name, "--no-pager"],
            stderr=subprocess.DEVNULL, text=True,
        )
        return {"name": name, "output": output, "running": True}
    except subprocess.CalledProcessError as e:
        return {"name": name, "output": e.output or "", "running": False}
    except FileNotFoundError:
        return {"name": name, "output": "", "running": False}


def is_enabled(name):
    """check if a service is enabled."""
    try:
        result = subprocess.run(
            ["systemctl", "is-enabled", name],
            capture_output=True, text=True,
        )
        return result.stdout.strip() == "enabled"
    except FileNotFoundError:
        return False


def service_summary():
    """get summary of service states."""
    services = list_services()
    active = sum(1 for s in services if s["active"] == "active")
    failed = sum(1 for s in services if s["sub"] == "failed")
    return {
        "total": len(services),
        "active": active,
        "failed": failed,
        "inactive": len(services) - active,
    }


if __name__ == "__main__":
    summary = service_summary()
    print(f"services: {summary}")
    services = list_services(active_only=True)
    print(f"\nactive services: {len(services)}")
    for s in services[:5]:
        print(f"  {s['name']}: {s['active']} ({s['sub']})")
