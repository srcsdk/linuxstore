#!/usr/bin/env python3
"""package dependency tree visualization"""

import subprocess


def get_dependencies(package, pkg_manager="pacman"):
    """get direct dependencies for a package."""
    cmd_map = {
        "pacman": ["pacman", "-Si", package],
        "apt": ["apt-cache", "depends", package],
        "dnf": ["dnf", "repoquery", "--requires", package],
    }
    cmd = cmd_map.get(pkg_manager)
    if not cmd:
        return []
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        if pkg_manager == "pacman":
            deps = []
            in_deps = False
            for line in result.stdout.split("\n"):
                if "Depends On" in line:
                    in_deps = True
                    parts = line.split(":")[1].strip()
                    if parts and parts != "None":
                        deps.extend(parts.split())
                elif in_deps and line.startswith(" "):
                    deps.extend(line.strip().split())
                elif in_deps:
                    break
            return [d.split(">")[0].split("<")[0].split("=")[0]
                    for d in deps]
        elif pkg_manager == "apt":
            return [
                line.strip().split()[-1]
                for line in result.stdout.split("\n")
                if "Depends:" in line
            ]
    except (subprocess.TimeoutExpired, OSError):
        pass
    return []


def build_tree(package, pkg_manager="pacman", depth=3, seen=None):
    """recursively build dependency tree."""
    if seen is None:
        seen = set()
    if package in seen or depth <= 0:
        return {"name": package, "deps": []}
    seen.add(package)
    deps = get_dependencies(package, pkg_manager)
    children = []
    for dep in deps[:10]:
        child = build_tree(dep, pkg_manager, depth - 1, seen)
        children.append(child)
    return {"name": package, "deps": children}


def format_tree(tree, prefix="", is_last=True):
    """format dependency tree as ascii art."""
    connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "
    lines = [prefix + connector + tree["name"]]
    child_prefix = prefix + ("    " if is_last else "\u2502   ")
    for i, child in enumerate(tree["deps"]):
        is_last_child = i == len(tree["deps"]) - 1
        lines.extend(format_tree(child, child_prefix, is_last_child))
    return lines


def print_tree(package, pkg_manager="pacman", depth=2):
    """print dependency tree for a package."""
    tree = build_tree(package, pkg_manager, depth)
    print(package)
    for i, child in enumerate(tree["deps"]):
        is_last = i == len(tree["deps"]) - 1
        for line in format_tree(child, "", is_last):
            print(line)


if __name__ == "__main__":
    import sys
    pkg = sys.argv[1] if len(sys.argv) > 1 else "python"
    print(f"dependency tree for: {pkg}")
    print_tree(pkg)
