#!/usr/bin/env python3
"""theme support for linuxstore gui"""

import os
import platform
import subprocess
from tkinter import ttk


THEMES = {
    "dark": {
        "bg": "#1e1e1e",
        "fg": "#cccccc",
        "accent": "#4ec9b0",
        "header_fg": "#ffffff",
        "dim": "#888888",
        "error": "#f44747",
        "frame_bg": "#1e1e1e",
        "entry_bg": "#2d2d2d",
        "entry_fg": "#cccccc",
        "highlight": "#264f78",
    },
    "light": {
        "bg": "#f5f5f5",
        "fg": "#333333",
        "accent": "#0078d4",
        "header_fg": "#111111",
        "dim": "#666666",
        "error": "#d32f2f",
        "frame_bg": "#f5f5f5",
        "entry_bg": "#ffffff",
        "entry_fg": "#333333",
        "highlight": "#cce5ff",
    },
}


def detect_system_theme():
    """detect the system's preferred color scheme"""
    system = platform.system()

    if system == "Linux":
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True, text=True, timeout=3
            )
            if "dark" in result.stdout.lower():
                return "dark"
            if "light" in result.stdout.lower() or "default" in result.stdout.lower():
                return "light"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # check kde
        kde_config = os.path.expanduser("~/.config/kdeglobals")
        if os.path.exists(kde_config):
            try:
                with open(kde_config) as f:
                    content = f.read()
                if "BreezeDark" in content:
                    return "dark"
            except OSError:
                pass

    elif system == "Darwin":
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True, timeout=3
            )
            if "dark" in result.stdout.lower():
                return "dark"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    return "dark"


def apply_theme(root, theme_name=None):
    """apply a theme to the application"""
    if theme_name is None:
        theme_name = detect_system_theme()

    theme = THEMES.get(theme_name, THEMES["dark"])

    root.configure(bg=theme["bg"])

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background=theme["bg"])
    style.configure("TLabel", background=theme["bg"],
                    foreground=theme["fg"], font=("monospace", 10))
    style.configure("Title.TLabel", font=("monospace", 14, "bold"),
                    foreground=theme["header_fg"])
    style.configure("TButton", font=("monospace", 10))
    style.configure("Tab.TButton", font=("monospace", 11), padding=8)
    style.configure("Install.TButton", font=("monospace", 9))

    return theme


def get_theme_names():
    """return list of available theme names"""
    return list(THEMES.keys())
