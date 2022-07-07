#!/usr/bin/env python3
"""arch user repository (aur) integration"""

import json
from urllib.request import urlopen, Request
from urllib.error import URLError


AUR_API = "https://aur.archlinux.org/rpc/v5"


def search(query, by="name-desc"):
    """search aur packages."""
    url = f"{AUR_API}/search/{query}?by={by}"
    data = _fetch(url)
    if not data:
        return []
    results = data.get("results", [])
    return [
        {
            "name": r.get("Name", ""),
            "version": r.get("Version", ""),
            "description": r.get("Description", ""),
            "votes": r.get("NumVotes", 0),
            "popularity": r.get("Popularity", 0),
            "maintainer": r.get("Maintainer", ""),
            "url": f"https://aur.archlinux.org/packages/{r.get('Name', '')}",
        }
        for r in results
    ]


def info(package_name):
    """get detailed info about an aur package."""
    url = f"{AUR_API}/info/{package_name}"
    data = _fetch(url)
    if not data or not data.get("results"):
        return None
    r = data["results"][0]
    return {
        "name": r.get("Name", ""),
        "version": r.get("Version", ""),
        "description": r.get("Description", ""),
        "votes": r.get("NumVotes", 0),
        "maintainer": r.get("Maintainer", ""),
        "depends": r.get("Depends", []),
        "make_depends": r.get("MakeDepends", []),
        "license": r.get("License", []),
        "url": r.get("URL", ""),
        "git_url": f"https://aur.archlinux.org/{r.get('Name', '')}.git",
    }


def _fetch(url):
    """fetch json from aur api."""
    try:
        req = Request(url, headers={"User-Agent": "linuxstore/1.0"})
        resp = urlopen(req, timeout=10)
        return json.loads(resp.read().decode())
    except (URLError, json.JSONDecodeError):
        return None


if __name__ == "__main__":
    results = search("yay")
    print(f"aur search 'yay': {len(results)} results")
    for r in results[:5]:
        print(f"  {r['name']:20s} v{r['version']:15s} votes:{r['votes']}")
    pkg = info("yay")
    if pkg:
        print(f"\nyay details:")
        print(f"  maintainer: {pkg['maintainer']}")
        print(f"  depends: {', '.join(pkg['depends'][:5])}")
