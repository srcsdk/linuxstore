#!/usr/bin/env python3
"""compare packages: alternatives, sizes, features"""

import subprocess


def find_alternatives(package_name):
    """find alternative packages to a given package."""
    alternatives_map = {
        "vim": ["neovim", "emacs", "nano", "kakoune", "helix"],
        "firefox": ["chromium", "brave-browser", "epiphany"],
        "bash": ["zsh", "fish", "dash"],
        "htop": ["btop", "glances", "atop", "bashtop"],
        "grep": ["ripgrep", "ack", "silversearcher-ag"],
        "find": ["fd", "fzf"],
        "cat": ["bat"],
        "ls": ["exa", "lsd"],
        "top": ["htop", "btop", "glances"],
        "docker": ["podman"],
        "git": ["mercurial", "fossil"],
    }
    lower = package_name.lower()
    if lower in alternatives_map:
        return alternatives_map[lower]
    for key, alts in alternatives_map.items():
        if lower in alts:
            return [key] + [a for a in alts if a != lower]
    return []


def compare_versions(pkg_a, pkg_b):
    """compare installed versions of two packages."""
    ver_a = _get_version(pkg_a)
    ver_b = _get_version(pkg_b)
    return {
        pkg_a: ver_a or "not installed",
        pkg_b: ver_b or "not installed",
    }


def _get_version(package):
    cmds = [
        ["pacman", "-Qi", package],
        ["dpkg", "-s", package],
        ["rpm", "-qi", package],
    ]
    for cmd in cmds:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "version" in line.lower() and ":" in line:
                        return line.split(":", 1)[1].strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


def compare_dependencies(pkg_a, pkg_b):
    """compare dependency counts of two packages."""
    deps_a = _get_deps(pkg_a)
    deps_b = _get_deps(pkg_b)
    common = set(deps_a) & set(deps_b)
    return {
        pkg_a: {"count": len(deps_a), "deps": deps_a},
        pkg_b: {"count": len(deps_b), "deps": deps_b},
        "common": list(common),
    }


def _get_deps(package):
    cmds = [
        (["pacman", "-Si", package], "Depends On"),
        (["apt-cache", "depends", package], "Depends:"),
    ]
    for cmd, key in cmds:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                deps = []
                for line in result.stdout.splitlines():
                    if key in line:
                        dep_str = line.split(":", 1)[1].strip()
                        deps.extend(d.strip().split(">")[0].split("<")[0].strip()
                                    for d in dep_str.split() if d != "None")
                    elif line.strip().startswith("Depends:"):
                        dep = line.strip().split(":", 1)[1].strip().split()[0]
                        deps.append(dep)
                return deps
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return []


if __name__ == "__main__":
    print("alternatives for vim:")
    for alt in find_alternatives("vim"):
        print(f"  {alt}")
    print("\nalternatives for grep:")
    for alt in find_alternatives("grep"):
        print(f"  {alt}")
