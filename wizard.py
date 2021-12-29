#!/usr/bin/env python3
"""startup wizard for first-time package source setup"""

import json
import os


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "store_config.json")


def load_config():
    """load store configuration."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(config):
    """save store configuration."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def is_first_run():
    """check if this is the first time running."""
    return not os.path.exists(CONFIG_FILE)


def run_wizard():
    """interactive first-time setup wizard."""
    print("welcome to linuxstore setup")
    print("=" * 40)
    config = {}
    from pkg_detect import detect_package_manager, get_distro_id
    pm = detect_package_manager()
    distro = get_distro_id()
    config["distro"] = distro
    config["package_manager"] = pm
    print(f"detected: {distro} with {pm}")
    from universal_pkgs import has_flatpak, has_snap
    config["flatpak"] = has_flatpak()
    config["snap"] = has_snap()
    print(f"flatpak: {'yes' if config['flatpak'] else 'no'}")
    print(f"snap: {'yes' if config['snap'] else 'no'}")
    config["sources"] = [pm] if pm else []
    if config["flatpak"]:
        config["sources"].append("flatpak")
    if config["snap"]:
        config["sources"].append("snap")
    config["setup_complete"] = True
    save_config(config)
    print(f"\nsetup complete. sources: {config['sources']}")
    return config


def reset_config():
    """reset configuration to trigger wizard on next run."""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)


if __name__ == "__main__":
    import sys
    if "--reset" in sys.argv:
        reset_config()
        print("config reset")
    elif is_first_run():
        run_wizard()
    else:
        config = load_config()
        print(f"configured: {config.get('distro')} "
              f"sources={config.get('sources', [])}")
