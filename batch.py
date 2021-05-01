#!/usr/bin/env python3
"""batch install and export for package lists"""

import json
import time


def load_package_list(filepath):
    """load package names from a text file (one per line)"""
    packages = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                packages.append(line)
    return packages


def save_package_list(packages, filepath):
    """save package names to a text file"""
    with open(filepath, "w") as f:
        f.write("# linuxstore package list\n")
        f.write(f"# exported {time.strftime('%Y-%m-%d %H:%M')}\n")
        for pkg in sorted(packages):
            f.write(f"{pkg}\n")


def batch_install(filepath, install_fn, progress_fn=None):
    """install packages from a list file.

    install_fn: callable(package_name) -> (success, message)
    progress_fn: optional callable(current, total, package_name, success)
    """
    packages = load_package_list(filepath)
    if not packages:
        return {"installed": 0, "failed": 0, "total": 0, "errors": []}

    results = {"installed": 0, "failed": 0, "total": len(packages), "errors": []}

    for i, pkg in enumerate(packages):
        success, msg = install_fn(pkg)
        if success:
            results["installed"] += 1
        else:
            results["failed"] += 1
            results["errors"].append({"package": pkg, "error": msg})

        if progress_fn:
            progress_fn(i + 1, len(packages), pkg, success)

    return results


def export_installed(list_fn, filepath):
    """export currently installed packages to a file.

    list_fn: callable() -> list of {"name": ..., "version": ...}
    """
    installed = list_fn()
    names = [pkg["name"] for pkg in installed]
    save_package_list(names, filepath)
    return len(names)


def format_batch_results(results):
    """format batch install results for display"""
    lines = [
        "batch install complete:",
        f"  installed: {results['installed']}/{results['total']}",
        f"  failed:    {results['failed']}",
    ]
    if results["errors"]:
        lines.append("  errors:")
        for err in results["errors"][:10]:
            lines.append(f"    {err['package']}: {err['error']}")
        if len(results["errors"]) > 10:
            lines.append(f"    ... and {len(results['errors']) - 10} more")
    return "\n".join(lines)


def confirm_uninstall(package_name, dependents):
    """check if other packages depend on this one and return a warning message.

    package_name: the package to uninstall.
    dependents: list of package names that depend on this package.
    returns a warning string if there are dependents, empty string otherwise.
    """
    if not dependents:
        return ""

    dep_list = ", ".join(dependents[:10])
    msg = f"warning: {len(dependents)} package(s) depend on {package_name}: {dep_list}"
    if len(dependents) > 10:
        msg += f" (and {len(dependents) - 10} more)"
    return msg


def load_json_list(filepath):
    """load a package list from json format"""
    with open(filepath) as f:
        data = json.load(f)
    if isinstance(data, list):
        return [p if isinstance(p, str) else p.get("name", "") for p in data]
    if isinstance(data, dict) and "packages" in data:
        return [p if isinstance(p, str) else p.get("name", "")
                for p in data["packages"]]
    return []


def save_json_list(packages, filepath, include_meta=True):
    """save a package list to json format"""
    data = {"packages": sorted(packages)}
    if include_meta:
        data["exported"] = time.strftime("%Y-%m-%d %H:%M")
        data["count"] = len(packages)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
