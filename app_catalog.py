#!/usr/bin/env python3
"""application catalog with categories and metadata"""

import json
import os


DEFAULT_CATEGORIES = {
    "gaming": {
        "essential": ["steam", "lutris"],
        "popular": ["heroic-games-launcher", "gamemode"],
    },
    "development": {
        "essential": ["git", "python", "nodejs", "docker"],
        "popular": ["code", "neovim", "postman"],
    },
    "security": {
        "essential": ["ufw", "clamav", "fail2ban"],
        "popular": ["wireshark", "nmap", "burpsuite"],
    },
    "entertainment": {
        "essential": [],
        "popular": ["spotify", "vlc", "obs-studio"],
    },
    "productivity": {
        "essential": ["libreoffice", "thunderbird"],
        "popular": ["obsidian", "zotero", "gimp"],
    },
    "system": {
        "essential": [
            "htop", "curl", "wget", "unzip", "base-devel",
        ],
        "popular": ["timeshift", "gparted", "neofetch"],
    },
    "communication": {
        "essential": [],
        "popular": ["discord", "signal-desktop", "slack-desktop"],
    },
}


class AppCatalog:
    """manage categorized application catalog."""

    def __init__(self, catalog_path=None):
        self.categories = dict(DEFAULT_CATEGORIES)
        self.apps = {}
        if catalog_path and os.path.isfile(catalog_path):
            self._load(catalog_path)

    def _load(self, path):
        """load catalog from json."""
        with open(path) as f:
            data = json.load(f)
        self.categories = data.get("categories", self.categories)
        self.apps = data.get("apps", {})

    def get_essential(self):
        """get all essential packages across categories."""
        essential = []
        for cat_data in self.categories.values():
            essential.extend(cat_data.get("essential", []))
        return sorted(set(essential))

    def get_popular(self):
        """get all popular packages across categories."""
        popular = []
        for cat_data in self.categories.values():
            popular.extend(cat_data.get("popular", []))
        return sorted(set(popular))

    def get_category(self, name):
        """get packages in a category."""
        cat = self.categories.get(name, {})
        return {
            "essential": cat.get("essential", []),
            "popular": cat.get("popular", []),
            "all": sorted(
                set(cat.get("essential", []) + cat.get("popular", []))
            ),
        }

    def search(self, query):
        """search for packages across all categories."""
        query = query.lower()
        results = []
        for cat_name, cat_data in self.categories.items():
            for pkg in cat_data.get("essential", []) + cat_data.get("popular", []):
                if query in pkg.lower():
                    results.append({"package": pkg, "category": cat_name})
        return results

    def add_app(self, name, category, tier="popular"):
        """add an app to the catalog."""
        if category not in self.categories:
            self.categories[category] = {"essential": [], "popular": []}
        self.categories[category][tier].append(name)

    def list_categories(self):
        """list all categories with counts."""
        return {
            name: len(data.get("essential", []) + data.get("popular", []))
            for name, data in self.categories.items()
        }

    def export(self, path):
        """save catalog to json."""
        with open(path, "w") as f:
            json.dump({
                "categories": self.categories,
                "apps": self.apps,
            }, f, indent=2)


if __name__ == "__main__":
    catalog = AppCatalog()
    cats = catalog.list_categories()
    for name, count in sorted(cats.items()):
        print(f"  {name}: {count} packages")
    essential = catalog.get_essential()
    print(f"\nessential ({len(essential)}): {', '.join(essential[:10])}")
