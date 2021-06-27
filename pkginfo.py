#!/usr/bin/env python3
"""package info panel with detailed description and dependencies"""

import subprocess
import tkinter as tk
from tkinter import ttk


def get_package_details(package_name, pkg_mgr_cmd):
    """get detailed package info from the package manager"""
    info_cmds = {
        "pacman": ["pacman", "-Si", package_name],
        "apt": ["apt-cache", "show", package_name],
        "dnf": ["dnf", "info", package_name],
        "brew": ["brew", "info", package_name],
        "winget": ["winget", "show", package_name],
    }
    args = info_cmds.get(pkg_mgr_cmd)
    if not args:
        return None

    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return None
        return parse_package_info(result.stdout, pkg_mgr_cmd)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def parse_package_info(output, pkg_mgr_cmd):
    """parse package manager output into a dict"""
    info = {}
    current_key = None
    for line in output.split("\n"):
        if not line.strip():
            continue
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            key = key.strip().lower()
            value = value.strip()
            info[key] = value
            current_key = key
        elif current_key and line.startswith(" "):
            info[current_key] += " " + line.strip()

    # normalize field names across package managers
    normalized = {
        "name": info.get("name", info.get("package", "")),
        "version": info.get("version", ""),
        "description": info.get("description", info.get("summary", "")),
        "url": info.get("url", info.get("homepage", "")),
        "license": info.get("licenses", info.get("license", "")),
        "size": info.get("installed size", info.get("size", "")),
        "depends": info.get("depends on", info.get("depends", "")),
    }
    return normalized


class PackageInfoPanel:
    """detailed package information panel"""

    def __init__(self, parent, pkg, pkg_mgr_cmd=None):
        self.window = tk.Toplevel(parent)
        self.window.title(f"package: {pkg['name']}")
        self.window.geometry("550x400")
        self.window.configure(bg="#1e1e1e")
        self.window.transient(parent)

        self._build_ui(pkg, pkg_mgr_cmd)

    def _build_ui(self, pkg, pkg_mgr_cmd):
        # header
        ttk.Label(self.window, text=pkg["name"],
                  font=("monospace", 14, "bold"),
                  foreground="#4ec9b0").pack(anchor="w", padx=15, pady=(15, 5))

        ttk.Label(self.window, text=pkg.get("desc", ""),
                  font=("monospace", 10), foreground="#cccccc",
                  wraplength=500).pack(anchor="w", padx=15, pady=5)

        ttk.Separator(self.window, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=15, pady=5)

        # details from package manager
        details = None
        if pkg_mgr_cmd:
            details = get_package_details(pkg["name"], pkg_mgr_cmd)

        info_frame = ttk.Frame(self.window)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=15)

        if details:
            fields = [
                ("version", details.get("version", "unknown")),
                ("license", details.get("license", "unknown")),
                ("size", details.get("size", "unknown")),
                ("url", details.get("url", "")),
            ]
            for label, value in fields:
                if value:
                    row = ttk.Frame(info_frame)
                    row.pack(fill=tk.X, pady=2)
                    ttk.Label(row, text=f"{label}:", width=12,
                              foreground="#888888").pack(side=tk.LEFT)
                    ttk.Label(row, text=value,
                              foreground="#cccccc").pack(side=tk.LEFT)

            # dependencies
            deps = details.get("depends", "")
            if deps:
                ttk.Label(info_frame, text="dependencies:",
                          foreground="#888888").pack(anchor="w", pady=(10, 2))

                dep_text = tk.Text(info_frame, height=5, bg="#2d2d2d",
                                   fg="#cccccc", font=("monospace", 9),
                                   wrap=tk.WORD)
                dep_text.pack(fill=tk.X, pady=2)
                dep_text.insert("1.0", deps)
                dep_text.configure(state=tk.DISABLED)
        else:
            ttk.Label(info_frame, text="package details not available",
                      foreground="#888888").pack(pady=20)

        # close button
        ttk.Button(self.window, text="close",
                   command=self.window.destroy).pack(pady=10)
