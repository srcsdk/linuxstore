#!/usr/bin/env python3
"""favorites/bookmarks for packages with persistent storage"""

import json
import os
from pathlib import Path

FAVORITES_DIR = Path.home() / ".config" / "linuxstore"
FAVORITES_FILE = FAVORITES_DIR / "favorites.json"


def load_favorites():
    """load saved favorites from disk"""
    if not FAVORITES_FILE.exists():
        return []
    try:
        with open(FAVORITES_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_favorites(favorites):
    """save favorites to disk"""
    FAVORITES_DIR.mkdir(parents=True, exist_ok=True)
    with open(FAVORITES_FILE, "w") as f:
        json.dump(favorites, f, indent=2)


def add_favorite(package_name, description=""):
    """add a package to favorites"""
    favorites = load_favorites()
    if any(f["name"] == package_name for f in favorites):
        return False
    favorites.append({"name": package_name, "desc": description})
    save_favorites(favorites)
    return True


def remove_favorite(package_name):
    """remove a package from favorites"""
    favorites = load_favorites()
    before = len(favorites)
    favorites = [f for f in favorites if f["name"] != package_name]
    if len(favorites) < before:
        save_favorites(favorites)
        return True
    return False


def is_favorite(package_name):
    """check if a package is in favorites"""
    return any(f["name"] == package_name for f in load_favorites())


def toggle_favorite(package_name, description=""):
    """toggle favorite status, returns new state"""
    if is_favorite(package_name):
        remove_favorite(package_name)
        return False
    add_favorite(package_name, description)
    return True


def get_favorites_as_packages():
    """return favorites in package list format"""
    return load_favorites()
