#!/usr/bin/env python3
"""system process management utilities"""

import subprocess


def list_processes(sort_by="memory"):
    """list running processes sorted by resource usage."""
    try:
        output = subprocess.check_output(
            ["ps", "aux", "--sort", f"-{sort_by[:3]}"],
            text=True,
        )
        processes = []
        for line in output.splitlines()[1:]:
            parts = line.split(None, 10)
            if len(parts) >= 11:
                processes.append({
                    "user": parts[0],
                    "pid": int(parts[1]),
                    "cpu": float(parts[2]),
                    "mem": float(parts[3]),
                    "command": parts[10],
                })
        return processes
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def find_process(name):
    """find processes matching a name."""
    processes = list_processes()
    return [p for p in processes if name.lower() in p["command"].lower()]


def process_tree():
    """get process tree."""
    try:
        output = subprocess.check_output(
            ["pstree", "-p"], text=True, stderr=subprocess.DEVNULL,
        )
        return output
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def top_cpu(n=5):
    """get top n processes by cpu usage."""
    processes = list_processes(sort_by="cpu")
    return processes[:n]


def top_memory(n=5):
    """get top n processes by memory usage."""
    processes = list_processes(sort_by="memory")
    return processes[:n]


def system_load():
    """get system load averages."""
    try:
        with open("/proc/loadavg") as f:
            parts = f.read().split()
        return {
            "1min": float(parts[0]),
            "5min": float(parts[1]),
            "15min": float(parts[2]),
        }
    except (FileNotFoundError, IndexError):
        return {}


if __name__ == "__main__":
    load = system_load()
    print(f"load: {load}")
    top = top_memory(5)
    print(f"\ntop memory ({len(top)}):")
    for p in top:
        print(f"  pid {p['pid']}: {p['mem']}% mem - "
              f"{p['command'][:50]}")
