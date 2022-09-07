#!/usr/bin/env python3
"""manage startup applications"""

import os
import configparser


AUTOSTART_DIR = os.path.expanduser("~/.config/autostart")


def list_startup_apps():
    """list desktop autostart applications."""
    apps = []
    system_dirs = ["/etc/xdg/autostart", AUTOSTART_DIR]
    for d in system_dirs:
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if name.endswith(".desktop"):
                path = os.path.join(d, name)
                app = _parse_desktop_file(path)
                if app:
                    app["source"] = "user" if d == AUTOSTART_DIR else "system"
                    apps.append(app)
    return apps


def _parse_desktop_file(path):
    """parse a .desktop file."""
    config = configparser.ConfigParser(interpolation=None)
    try:
        config.read(path)
    except configparser.Error:
        return None
    if "Desktop Entry" not in config:
        return None
    entry = config["Desktop Entry"]
    hidden = entry.get("Hidden", "false").lower() == "true"
    no_display = entry.get("NoDisplay", "false").lower() == "true"
    return {
        "name": entry.get("Name", os.path.basename(path)),
        "exec": entry.get("Exec", ""),
        "comment": entry.get("Comment", ""),
        "enabled": not hidden,
        "visible": not no_display,
        "path": path,
    }


def disable_startup(name):
    """disable a startup application."""
    apps = list_startup_apps()
    for app in apps:
        if app["name"].lower() == name.lower():
            config = configparser.ConfigParser(interpolation=None)
            config.read(app["path"])
            config["Desktop Entry"]["Hidden"] = "true"
            with open(app["path"], "w") as f:
                config.write(f)
            return True
    return False


def enable_startup(name):
    """enable a startup application."""
    apps = list_startup_apps()
    for app in apps:
        if app["name"].lower() == name.lower():
            config = configparser.ConfigParser(interpolation=None)
            config.read(app["path"])
            config["Desktop Entry"]["Hidden"] = "false"
            with open(app["path"], "w") as f:
                config.write(f)
            return True
    return False


if __name__ == "__main__":
    apps = list_startup_apps()
    print(f"startup applications: {len(apps)}")
    for app in apps:
        status = "enabled" if app["enabled"] else "disabled"
        print(f"  [{status:8s}] {app['name']:25s} {app['exec'][:40]}")
