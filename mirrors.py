#!/usr/bin/env python3
"""mirror speed testing and selection"""

import subprocess
import time
from urllib.request import urlopen
from urllib.error import URLError


def test_mirror_speed(url, timeout=10):
    """test download speed of a mirror."""
    start = time.time()
    try:
        resp = urlopen(url, timeout=timeout)
        data = resp.read(1024 * 100)
        elapsed = time.time() - start
        if elapsed > 0:
            speed = len(data) / elapsed / 1024
            return {"url": url, "speed_kbps": round(speed, 1), "ok": True}
        return {"url": url, "speed_kbps": 0, "ok": True}
    except (URLError, OSError):
        return {"url": url, "speed_kbps": 0, "ok": False}


def get_pacman_mirrors():
    """get pacman mirror list."""
    mirrorlist = "/etc/pacman.d/mirrorlist"
    mirrors = []
    try:
        with open(mirrorlist) as f:
            for line in f:
                line = line.strip()
                if line.startswith("Server"):
                    url = line.split("=", 1)[1].strip()
                    mirrors.append(url)
                elif line.startswith("#Server"):
                    url = line[1:].split("=", 1)[1].strip()
                    mirrors.append(url)
    except OSError:
        pass
    return mirrors


def rank_mirrors(mirrors, test_count=5):
    """rank mirrors by speed."""
    results = []
    for mirror in mirrors[:test_count]:
        test_url = mirror.replace("$repo/os/$arch", "core/os/x86_64/core.db")
        result = test_mirror_speed(test_url)
        result["mirror"] = mirror
        results.append(result)
    results.sort(key=lambda r: r["speed_kbps"], reverse=True)
    return results


if __name__ == "__main__":
    mirrors = get_pacman_mirrors()
    print(f"found {len(mirrors)} mirrors")
    if mirrors:
        ranked = rank_mirrors(mirrors[:3])
        for r in ranked:
            status = f"{r['speed_kbps']} KB/s" if r["ok"] else "failed"
            print(f"  {status:15s} {r['mirror'][:60]}")
