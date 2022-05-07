#!/usr/bin/env python3
"""manage package repositories"""

import subprocess
import os


def list_repos():
    """list configured package repositories."""
    methods = [_list_apt_repos, _list_pacman_repos, _list_dnf_repos]
    for method in methods:
        repos = method()
        if repos:
            return repos
    return []


def _list_apt_repos():
    sources_dir = "/etc/apt/sources.list.d"
    sources_file = "/etc/apt/sources.list"
    repos = []
    if os.path.isfile(sources_file):
        with open(sources_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    repos.append({"source": sources_file, "entry": line})
    if os.path.isdir(sources_dir):
        for name in os.listdir(sources_dir):
            path = os.path.join(sources_dir, name)
            if name.endswith(".list") and os.path.isfile(path):
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            repos.append({"source": name, "entry": line})
    return repos


def _list_pacman_repos():
    conf = "/etc/pacman.conf"
    if not os.path.isfile(conf):
        return []
    repos = []
    current = None
    with open(conf) as f:
        for line in f:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                name = line[1:-1]
                if name != "options":
                    current = name
            elif current and line.startswith("Server"):
                url = line.split("=", 1)[1].strip()
                repos.append({"name": current, "url": url})
                current = None
    return repos


def _list_dnf_repos():
    repo_dir = "/etc/yum.repos.d"
    if not os.path.isdir(repo_dir):
        return []
    repos = []
    for name in os.listdir(repo_dir):
        if name.endswith(".repo"):
            path = os.path.join(repo_dir, name)
            repo_info = {"file": name}
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("name="):
                        repo_info["name"] = line.split("=", 1)[1]
                    elif line.startswith("baseurl="):
                        repo_info["url"] = line.split("=", 1)[1]
                    elif line.startswith("enabled="):
                        repo_info["enabled"] = line.split("=", 1)[1] == "1"
            repos.append(repo_info)
    return repos


def add_ppa(ppa_name):
    """add a ppa repository (ubuntu/debian)."""
    try:
        result = subprocess.run(
            ["add-apt-repository", "-y", f"ppa:{ppa_name}"],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


if __name__ == "__main__":
    repos = list_repos()
    print(f"configured repositories: {len(repos)}")
    for r in repos[:10]:
        if "name" in r:
            print(f"  {r['name']}: {r.get('url', '')}")
        elif "entry" in r:
            print(f"  {r['entry'][:70]}")
