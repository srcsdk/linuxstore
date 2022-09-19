#!/usr/bin/env python3
"""package compatibility checking across distributions"""

import json
import os


PACKAGE_MAP = {
    "build-essential": {
        "arch": "base-devel",
        "fedora": "gcc make",
        "ubuntu": "build-essential",
        "debian": "build-essential",
        "opensuse": "devel_basis",
    },
    "python3": {
        "arch": "python",
        "fedora": "python3",
        "ubuntu": "python3",
        "debian": "python3",
        "opensuse": "python3",
    },
    "git": {
        "arch": "git",
        "fedora": "git",
        "ubuntu": "git",
        "debian": "git",
        "opensuse": "git",
    },
    "docker": {
        "arch": "docker",
        "fedora": "docker-ce",
        "ubuntu": "docker.io",
        "debian": "docker.io",
        "opensuse": "docker",
    },
    "nodejs": {
        "arch": "nodejs",
        "fedora": "nodejs",
        "ubuntu": "nodejs",
        "debian": "nodejs",
        "opensuse": "nodejs",
    },
    "ffmpeg": {
        "arch": "ffmpeg",
        "fedora": "ffmpeg",
        "ubuntu": "ffmpeg",
        "debian": "ffmpeg",
        "opensuse": "ffmpeg-4",
    },
}


class CompatibilityChecker:
    """check and map package names across distributions."""

    def __init__(self, distro=None):
        self.distro = distro
        self.package_map = dict(PACKAGE_MAP)
        self.custom_map = {}

    def translate(self, package_name, target_distro=None):
        """translate package name to target distribution."""
        distro = target_distro or self.distro
        if not distro:
            return package_name
        mapping = self.package_map.get(package_name, {})
        return mapping.get(distro, package_name)

    def translate_list(self, packages, target_distro=None):
        """translate a list of package names."""
        return [self.translate(p, target_distro) for p in packages]

    def is_available(self, package_name, distro=None):
        """check if package has a known mapping."""
        d = distro or self.distro
        mapping = self.package_map.get(package_name, {})
        return d in mapping

    def add_mapping(self, package_name, mappings):
        """add custom package name mapping."""
        if package_name not in self.package_map:
            self.package_map[package_name] = {}
        self.package_map[package_name].update(mappings)

    def find_alternatives(self, package_name):
        """find all known names for a package across distros."""
        mapping = self.package_map.get(package_name, {})
        return dict(mapping)

    def export_map(self, filepath):
        """export package map to json."""
        with open(filepath, "w") as f:
            json.dump(self.package_map, f, indent=2)

    def load_map(self, filepath):
        """load custom package map from json."""
        if os.path.isfile(filepath):
            with open(filepath) as f:
                custom = json.load(f)
            self.package_map.update(custom)


if __name__ == "__main__":
    checker = CompatibilityChecker(distro="arch")
    packages = ["build-essential", "python3", "docker", "nodejs"]
    for pkg in packages:
        translated = checker.translate(pkg)
        print(f"  {pkg} -> {translated}")
